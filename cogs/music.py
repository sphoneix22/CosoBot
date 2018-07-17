import asyncio

import discord
from async_timeout import timeout
from discord.ext import commands
from googleapiclient.discovery import build
from youtube_dl import YoutubeDL

API = 'youtube'
API_V = 'v3'

ytdl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "./data/cache/music/%(extractor)s-%(id)s.%(ext)s",
    "quiet": True
}

ytdl = YoutubeDL(ytdl_opts)


class YTDL:
    """
    Class with all YT search/download functions
    """

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
    def downloader(cls, id):
        """
        Downloads a song from youtube and creates FFmpeg player with it.
        It also returns data of the song.
        ------------------
        :param id: (Everything that stays after www.youtube.com/watch?v=)
        :return: discord.FFmpegplayer, list
        """

        URL = "https://www.youtube.com/watch?v={}"
        data = ytdl.extract_info(URL.format(id))
        filename = ytdl.prepare_filename(data)
        return discord.FFmpegPCMAudio(filename), data


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

        self.np = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Main player loop"""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for song. If timeout closes connection
                async with timeout(120):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                if self in self._cog.players.values():
                    return self.destroy(self._guild)
                return

            self.current = source

            self._guild.voice_client.play(source[0], after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f"Ora suono: **{source[1]['title']}**")

            await self.next.wait()

            source[0].cleanup()  # Cleanup FFmpeg process
            self.current = None  # Not playing at the moment

            try:
                await self.np.delete()  # No longer playing
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect"""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music:
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

    async def join(self, ctx):
        if ctx.message.author.voice is None:
            return await ctx.send("Hey, entra in un canale!")
        if ctx.voice_client is None:
            return await ctx.message.author.voice.channel.connect()
        else:
            return await ctx.voice_client.move_to(ctx.message.author.voice.channel)

    async def get_msg(self, result: list):
        """
        Creates a choose msg from a list of videos.

        :param result: list
        :return: str
        """
        msg = "Risultati su Youtube: \n"
        for video in result:
            msg += f"{result.index(video)+1}-- **{video['snippet']['title']}** \n"
        msg += "**Scrivi il numero della canzone che vuoi ascoltare**"
        return msg

    async def skip_counter(self, users, ctx):
        if len(users) - 1 % 2 == 0:
            max_limit = len(users) - 1 / 2
        else:
            max_limit = len(users) // 2

        try:
            if ctx.message.author.id not in self.skips[ctx.guild.id]:
                self.skips[ctx.guild.id].append(ctx.message.author.id)
            if max_limit == len(self.skips[ctx.guild.id]):
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

    @commands.command(name='play')
    async def play(self, ctx):
        result = await YTDL.YT_search(ctx.message.content[6:], self.bot.secrets['google_api_key'])
        choose_msg = await self.get_msg(result)
        await ctx.send(choose_msg)

        # Now we have sent the message to choose the video from, let's wait for an asnwer

        def check(m):
            """
            Checks if the message is sent by the user and if the number is valid
            """
            return m.author == ctx.message.author and m.channel == ctx.message.channel and int(m.content) in range(1,len(result) + 1)

        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
            await ctx.send("Ok, canzone scelta.")
            id = result[int(msg.content) - 1]['id']['videoId']  # gets video id by the index of the list
            vc = await self.join(ctx)
            song = YTDL.downloader(id)
            player = self.get_player(ctx)
            await player.queue.put(song)
        except asyncio.TimeoutError:
            await ctx.send("Ok, non la suono più")

    @commands.command(name='nowplaying', aliases=['np', 'song'])
    async def nowplaying_(self, ctx):
        if ctx.guild.id in self.players.keys():
            np = self.players[ctx.guild.id].np
            return await ctx.send(np.content)
        return

    @commands.command(name='skip')
    async def skip_(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return

        for ruolo in ctx.message.author.roles:
            if ruolo.name == "DJ" or ruolo.name == "dj":
                await ctx.send(f"Ora skippo solo perchè tu sei un DJ, {ctx.message.author.mention}!")
                return vc.stop()
        try:
            if ctx.message.author.id in self.skips[ctx.guild.id]:
                return
        except KeyError:
            pass

        await self.skip_counter(vc.channel.members, ctx)

    @commands.command(name='pause')
    async def pause_(self, ctx):
        """
        Pause the current playing song.
        """
        vc = ctx.voice_client

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

        if not vc or not vc.is_paused():
            return await ctx.send(f"Ma che vuoi? {ctx.message.author.mention}")
        elif vc.is_playing():
            return

        vc.resume()
        await ctx.send(f"Ho ricominciato a suonare, {ctx.message.author.mention}")

    @commands.command(name='stop')
    async def stop_(self, ctx):
        """
        Stops and deletes the player.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(f"Ma che vuoi? {ctx.message.author.mention}")

        await self.cleanup(ctx.guild)


def setup(bot):
    bot.add_cog(Music(bot=bot))
