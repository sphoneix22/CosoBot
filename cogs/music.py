import asyncio

import discord
import datetime
from async_timeout import timeout
from discord.ext import commands
from googleapiclient.discovery import build
from youtube_dl import YoutubeDL
from time import time
from html import unescape

API = 'youtube'
API_V = 'v3'

ytdl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "./data/cache/music/%(extractor)s-%(id)s.%(ext)s",
    "quiet": True
}

ytdl = YoutubeDL(ytdl_opts)


class YTDL(discord.PCMVolumeTransformer):
    """
    Class with all YT search/download functions
    """

    def __init__(self, source):
        super().__init__(source)

    @classmethod
    async def YT_search(cls, query: str, api: str):
        """
        Searches on youtube 5 videos and return a list of dictionaries with data.
        -----------------------------
        :param query: str (Song to search)
        :param api: str (api key)
        :return: list
        """
        youtube = build(API, API_V, developerKey=api)
        search = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            maxResults=5
        ).execute()
        return search['items']

    @classmethod
    def downloader(cls, video_id, silent=False):
        """
        Downloads a song from youtube and creates FFmpeg player with it.
        It also returns data of the song.
        ------------------
        :param silent:
        :param video_id: (Everything that stays after www.youtube.com/watch?v=)
        :return: discord.FFmpegplayer, list
        """

        URL = "https://www.youtube.com/watch?v={}"
        data = ytdl.extract_info(URL.format(video_id))
        filename = ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename)), data, silent

    @classmethod
    def downloader_fromurl(cls, url: str, silent=False):
        data = ytdl.extract_info(url)
        filename = ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename)), data, silent

    @classmethod
    def get_channel_pic(cls, channel_id: str, api_key: str):
        youtube = build(API, API_V, developerKey=api_key)
        search = youtube.search().list(
            part="snippet",
            q=channel_id,
            type="channel",
            maxResults=1
        ).execute()

        return search['items'][0]['snippet']['thumbnails']['default']['url']


class MusicPlayer:
    """
    Class assigned to each server.
    The class implements a queue and loop to handle songs.

    """

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.data = None
        self.start_time = None
        self.current = None
        self.volume = 0.5

        self.np = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Main player loop"""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for song. If timeout closes connection
                if self.queue.empty():
                    await self._channel.send("Coda terminata. Resto in ascolto per un altro minuto, poi ciao!")
                async with timeout(60):
                    source, data, silent = await self.queue.get()
            except asyncio.TimeoutError:
                await self._channel.send("Nessuna canzone aggiunta alla coda. Esco dal canale...")
                if self in self._cog.players.values():
                    return self.destroy(self._guild)
                return

            source.volume = self.volume

            self.current = source

            self.data = data

            self.start_time = time()

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            if not silent:
                self.np = await self._channel.send(
                    f"Ora sto suonando: **{data['title']}** - {data['uploader']} ({datetime.timedelta(seconds=data['duration'])})")

            await self.next.wait()

            source.cleanup()  # Cleanup FFmpeg process
            self.current = None  # Not playing at the moment

            try:
                await self.np.delete()  # No longer playing
            except discord.HTTPException:
                pass
            except AttributeError:
                pass

    def destroy(self, guild):
        """Disconnect"""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.skips = {}

    async def cleanup(self, guild):
        await guild.voice_client.disconnect()
        del self.players[guild.id]

    def get_player(self, ctx):
        """Retrieve guild player or generate one"""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @staticmethod 
    async def join(ctx):
        if ctx.message.author.voice is None:
            return await ctx.send("Hey, entra in un canale!")
        if ctx.voice_client is None:
            return await ctx.message.author.voice.channel.connect()
        else:
            return await ctx.voice_client.move_to(ctx.message.author.voice.channel)

    @staticmethod
    async def get_msg(result: list):
        """
        Creates a choose msg from a list of videos.

        :param result: list
        :return: str
        """
        msg = "Risultati su Youtube: \n"
        counter = 0

        for video in result:
            msg += f"{result.index(video)+1}-- **{unescape(video['snippet']['title'])}** \n"
            counter += 1

        return msg, counter

    async def skip_counter(self, users, ctx):
        if users % 2 == 0:
            max_limit = users / 2
        else:
            max_limit = users // 2

        try:
            if ctx.message.author.id not in self.skips[ctx.guild.id]:
                self.skips[ctx.guild.id].append(ctx.message.author.id)
            if max_limit <= len(self.skips[ctx.guild.id]):
                await ctx.send("Ok, skippo...")
                del self.skips[ctx.guild.id]
                ctx.voice_client.stop()
            else:
                await ctx.send(f"Mancano ancora {max_limit-len(self.skips[ctx.guild.id])+1} voti.")

        except KeyError:
            if max_limit == 1:
                await ctx.send(f"Ok, skippo...")
                return ctx.voice_client.stop()
            self.skips[ctx.guild.id] = [ctx.message.author.id]
            await ctx.send(f"Mancano ancora {max_limit-1} voti.")

    async def link_player(self, ctx, query, silent=False):
        if silent:
            try:
                await ctx.message.author.send("Tento di scaricare dal link...")
                song = YTDL.downloader_fromurl(query, silent=silent)
                vc = await self.join(ctx)
                player = self.get_player(ctx)
                await player.queue.put(song)
            except:
                return await ctx.message.author.send("Errore nel download. Sei sicuro che il link sia corretto?")
        else:
            link_msg = await ctx.send(f"Tento di scaricare dal link {query}...")
            try:
                song = YTDL.downloader_fromurl(query, silent=silent)
                vc = await self.join(ctx)
                player = self.get_player(ctx)
                await player.queue.put(song)
                return await link_msg.delete()
            except Exception:
                return await ctx.send(f"Link non valido, {ctx.message.author.mention}")

    async def play(self, ctx, silent=False):
        if ctx.message.author.voice is None:
            return await ctx.send(f"Entra in un canale, {ctx.message.author.mention}")

        if silent:
            query = ""
            await ctx.message.delete()
        else:
            query = ctx.message.content[6:]

        if query.startswith(("http", "www.")):
            return await self.link_player(ctx, query, silent=silent)

        if silent:
            dm_message = await ctx.message.author.send("Scrivimi ciò che vuoi suonare.\n (Heisenberg o Bari Vecchia?)")

            def silent_check(m):
                return m.author == ctx.message.author and m.channel == dm_message.channel

            try:
                query_msg = await self.bot.wait_for('message', check=silent_check)
            except asyncio.TimeoutError:
                return

            query = query_msg.content

            if query.startswith(("http", "www.")):
                return await self.link_player(ctx, query, silent=True)

            result = await YTDL.YT_search(query, self.bot.secrets['google_api_key'])
            msg, n_videos = await self.get_msg(result)
            try:
                choose_msg = await ctx.message.author.send(msg)
            except:
                return
        else:
            result = await YTDL.YT_search(query, self.bot.secrets['google_api_key'])
            msg, n_videos = await self.get_msg(result)
            choose_msg = await ctx.send(msg)

        emojis = {1: "\U00000031\U000020e3", 2: "\U00000032\U000020e3", 3: "\U00000033\U000020e3",
                  4: "\U00000034\U000020e3", 5: "\U00000035\U000020e3", 'x': '\U0000274c'}

        for video in range(1, n_videos + 1):
            await choose_msg.add_reaction(emojis[video])
        await choose_msg.add_reaction(emojis['x'])

        # Now we have sent the message to choose the video from, let's wait for an asnwer

        def check(reaction, user):
            """
            Checks if the message is sent by the user and if the reaction is valid
            """
            return str(
                reaction) in emojis.values() and user == ctx.message.author and reaction.message.id == choose_msg.id

        try:
            rct, usr = await self.bot.wait_for("reaction_add", timeout=60, check=check)
        except asyncio.TimeoutError:
            return await choose_msg.delete()
        if str(rct) == '\U0000274c' and silent:
            return await choose_msg.delete()
        elif str(rct) == '\U0000274c' and not silent:
            await ctx.message.delete()
            return await choose_msg.delete()

        if not silent:
            success_msg = await ctx.send("Ok, canzone scelta.")
        await choose_msg.delete()

        index = 0

        for emoji in emojis.values():
            if emoji == str(rct.emoji):
                index = list(emojis.values()).index(emoji)

        video_id = result[index]['id']['videoId']  # gets video id by the index of the list
        song = YTDL.downloader(video_id, silent=silent)
        song[1]['requester'] = ctx.message.author
        vc = await self.join(ctx)
        if ctx.guild.voice_client.is_playing() and not silent:
            await ctx.send(f"{ctx.message.author.mention} ha aggiunto **{song[1]['title']}** alla coda.")
        player = self.get_player(ctx)
        await player.queue.put(song)
        if not silent:
            await success_msg.delete()

    @commands.command(name='play')
    async def play_(self, ctx):
        await self.play(ctx)

    @commands.command(name="playsilent")
    async def play_silent(self, ctx):
        await self.play(ctx, silent=True)

    @commands.command(name='volume', aliases=['vol'])
    async def volume_(self, ctx, volume: float):
        if not ctx.guild.voice_client.is_connected():
            return
        if not 0 < volume < 101:
            return await ctx.send(f"Devi indicare un valore in percentuale tra 1 e 100, {ctx.message.author.mention}")

        player = self.get_player(ctx)

        vc = ctx.guild.voice_client

        if vc.source:
            vc.source.volume = volume / 100

        player.volume = volume / 100

        await ctx.send(f"{ctx.message.author.mention} ha cambiato il volume a {volume}%")
        await ctx.message.delete()

    @commands.command(name='nowplaying', aliases=['np', 'song'])
    async def nowplaying_(self, ctx):
        await ctx.message.delete()
        if not ctx.guild.voice_client.is_playing():
            return

        if ctx.guild.id in self.players.keys():
            player = self.players[ctx.guild.id]
            song_data = player.data
            start_time = player.start_time
            elapsed_time = int(time() - start_time)

            embed = discord.Embed(title=song_data['title'],
                                  url="https://www.youtube.com/watch?v={}".format(song_data['id']),
                                  color=0x338DFF)
            embed.set_thumbnail(url=song_data['thumbnail'])
            embed.set_author(name=song_data['uploader'],
                             url="https://www.youtube.com/channel/{}".format(song_data["uploader_url"]),
                             icon_url=YTDL.get_channel_pic(song_data['uploader'], self.bot.secrets["google_api_key"]))
            embed.add_field(name="Time", value="{}/{}".format(datetime.timedelta(seconds=elapsed_time),
                                                              datetime.timedelta(seconds=song_data["duration"])))
            embed.set_footer(text=f"Canzone richiesta da {str(song_data['requester'])}",
                             icon_url=song_data['requester'].avatar_url)

            await ctx.send(embed=embed)

    @commands.command(name='queue')
    async def queue_(self, ctx):
        if not ctx.guild.voice_client.is_playing():
            return
        player = self.get_player(ctx)
        queue = player.queue
        try:
            embed = discord.Embed(title="Coda", color=0x338DFF)
            embed.set_footer(text=f"Richiesto da {str(ctx.author)}", icon_url=ctx.author.avatar_url)
            for song in queue._queue:
                data = song[1]
                embed.add_field(name=queue._queue.index(song) + 1, value=f"**{data['title']}** -- {data['uploader']} "
                                                                         f"({datetime.timedelta(seconds=data['duration'])})"
                                                                         f"\nRichiesta da **{str(data['requester'])}**")
            await ctx.send(embed=embed)
        except KeyError:
            await ctx.send("Coda vuota")

    @commands.command(name='skip')
    async def skip_(self, ctx):
        if not ctx.guild.voice_client.is_playing():
            return
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return

        for ruolo in ctx.message.author.roles:
            if ruolo.name == "DJ":
                await ctx.send(f"Ora skippo solo perchè tu sei un DJ, {ctx.message.author.mention}!")
                await ctx.message.delete()
                return vc.stop()
        try:
            if ctx.message.author.id in self.skips[ctx.guild.id]:
                return await ctx.message.delete()
        except KeyError:
            pass

        await ctx.message.delete()
        await self.skip_counter(len(vc.channel.members)-1, ctx)

    @commands.command(name='pause')
    async def pause_(self, ctx):
        """
        Pause the current playing song.
        """
        vc = ctx.voice_client
        await ctx.message.delete()

        if not vc or not vc.is_playing():
            return await ctx.send(f"Ma che vuoi? {ctx.message.author.mention}")
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f"Ho messo in pausa, {ctx.message.author.mention}.")

    @commands.command(name='resume')
    async def resume_(self, ctx):
        """
        Resume the current paused song.
        """
        vc = ctx.voice_client

        await ctx.message.delete()

        if not vc or not vc.is_paused():
            return await ctx.send(f"Ma che vuoi? {ctx.message.author.mention}")
        elif vc.is_playing():
            return

        vc.resume()
        await ctx.send(f"Ho ricominciato a suonare, {ctx.message.author.mention}")

    @commands.command(name='stop')
    @commands.has_role("DJ")
    async def stop_(self, ctx):
        """
        Stops and deletes the player.
        """
        vc = ctx.voice_client

        await ctx.message.delete()

        if not vc or not vc.is_connected():
            return await ctx.send(f"Ma che vuoi? {ctx.message.author.mention}")

        await self.cleanup(ctx.guild)


def setup(bot):
    bot.add_cog(Music(bot=bot))
