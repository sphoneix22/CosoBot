import asyncio

import discord
from googleapiclient.discovery import build
from discord.ext import commands
import youtube_dl

API = "youtube"
API_VERSION = "v3"

ytdl_opts = {
    "format" : "bestaudio/best",
    "outtmpl" : "./data/cache/music/%(extractor)s-%(id)s.%(ext)s",
    "quiet" : False
}

ytdl = youtube_dl.YoutubeDL(ytdl_opts)

class Music:
    def __init__(self,bot):
        self.bot = bot

    def initialize_api(self):
        return build(API,API_VERSION,developerKey=self.bot.secrets["google_api_key"])

    def YT_search(self, query):
        youtube = self.initialize_api()
        search = youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=5
                ).execute()
        return search['items']

    async def join(self,channel):
        return await channel.connect()

    @commands.command(name='play')
    async def testing(self,ctx):
        result = self.YT_search(ctx.message.content[6:])
        msg = "Risultati su Youtube: \n"
        for video in result:
            msg += f"{result.index(video)+1}-- **{video['snippet']['title']}** \n"
        msg += "**Scrivi il numero della canzone che vuoi ascoltare**"
        await ctx.send(msg)
        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel and int(m.content) in range(len(result))
        try:
            msg = await self.bot.wait_for("message",timeout=60, check=check)
            await ctx.send("Ok, ora la scarico...")
            print(msg.content)
            hey = downloader(result[int(msg.content)-1]['id']['videoId'])
        except asyncio.TimeoutError:
            await ctx.send("Tempo scaduto!")
        #todo playing


def downloader(id):
        URL = "https://www.youtube.com/watch?v={}"
        data = ytdl.extract_info(URL.format(id))
        filename = ytdl.prepare_filename(data)
        return discord.FFmpegPCMAudio(filename), data


def setup(client):
    client.add_cog(Music(client))