from google_images_download import google_images_download
import discord
from discord.ext import commands
import os

response = google_images_download.googleimagesdownload()


class GID():
    @classmethod
    def downloader(cls,keyword):
        opts = {'keywords':keyword,
                'limit':1,
                'output_directory':f"{os.path.dirname(os.getcwd())}/data/cache/images",
                'no_directory':True}
        path = response.download(opts)
        return path

class Google():
    def __init__(self,client):
        self.bot = client

    @commands.command('image')
    @commands.cooldown(2,10,commands.BucketType.guild)
    async def image(self,ctx):
        async with ctx.typing():
            query = ctx.message.content[7:]
            path = GID.downloader(query)
            actual_path = path[query][0]
            await ctx.send("**{}**".format(query),file=discord.File(actual_path))


def setup(client):
    client.add_cog(Google(client))