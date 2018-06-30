import discord
import youtube_dl
from discord.ext import commands

ytdl_format_options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'outtmpl': './data/cache/music/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# TODO Creare qualcosa che elimina i vecchi file audio
# TODO Creare queue

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDL():
    @classmethod
    async def from_url(cls, url):
        data = ytdl.extract_info(url=url)
        filename = ytdl.prepare_filename(data)
        return discord.FFmpegPCMAudio("./{}".format(filename)), data


class Music():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='play')
    async def info(self, ctx):
        if ctx.voice_client is not None:
            vc = await ctx.voice_client.move_to(ctx.message.author.voice.channel)
        else:
            vc = await ctx.message.author.voice.channel.connect()
        url = ctx.message.content[6:]
        source = await YTDL.from_url(url)
        self.title = source[1]['title']
        await ctx.send("Ok, ora canto '**{}**', solo per te <3".format(self.title))
        await vc.play(source[0])

    @commands.command(name='stop')  # TODO Capire perchè sto coso non funziona
    async def stop(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice.disconnect()
        else:
            ctx.send("Ma cosa vuoi?")

    @commands.command(name='pause')
    async def stop(self, ctx):
        if ctx.voice_client.is_playing():
            await ctx.send("Ho stoppato **{}**".format(self.title))
            await ctx.voice_client.pause()
        else:
            await ctx.send("Ma che vuoi? Sono zitto!")

    @commands.command(name='resume')
    async def resume(self, ctx):
        if ctx.voice_client.is_playing():
            await ctx.send("Stai zitto che sto già parlando!")
        elif ctx.voice_client.is_paused():
            await ctx.send("**{}** è ripartito.".format(self.title))
            await ctx.voice_client.resume()
        else:
            await ctx.send("Così, a caso!")


def setup(bot):
    bot.add_cog(Music(bot=bot))
