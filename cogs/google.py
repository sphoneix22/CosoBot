import os

import discord
from discord.ext import commands
from google_images_download import google_images_download

import wikipedia

response = google_images_download.googleimagesdownload()


class GID():
    @classmethod
    def downloader(cls, keyword):
        opts = {'keywords': keyword,
                'limit': 1,
                'output_directory': f"{os.getcwd()}/data/cache/images",
                'no_directory': True,
                'delay': 3,
                'extract-metadata': True,
                'format':'jpg'}
        path = response.download(opts)
        return path


class Google():
    def __init__(self, client):
        self.bot = client

    @commands.command('image')
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def image(self, ctx):
        async with ctx.typing():
            query = ctx.message.content[7:]
            path = GID.downloader(query)
            actual_path = path[query][0]
            await ctx.send("**{}**".format(query), file=discord.File(actual_path))

    # todo text search

    @commands.command(name='wiki')
    @commands.cooldown(1,2,commands.BucketType.user)
    async def wiki(self,ctx):
        wikipedia.set_lang('it')
        query = ctx.message.content[6:]
        async with ctx.typing():
            try:
                page = wikipedia.page(query)
                sum = wikipedia.summary(query,sentences=3)
                embed = discord.Embed(title=f"**{page.title}**",url=page.url,colour=discord.Colour(0x8f8f87),
                                      description=sum)
                def get_image(page):
                    try:
                        for image in page.images:
                            if image[-3:] == 'jpg' or image[-3:] == 'png':
                                return str(image)
                    except:
                        return None
                image = get_image(page)
                if image is not None:
                    embed.set_thumbnail(url=image)
                embed.set_footer(text='Powered by Wikipedia API',
                                 icon_url='https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/1122px-Wikipedia-logo-v2.svg.png')
                await ctx.send(embed=embed)
            except wikipedia.exceptions.DisambiguationError: #todo fix this shit
                await ctx.send("Qui c'è un errore di disambiguazione, al momento non riesco a risolverlo. Scusa se sono "
                         "stupido :frowning:")
            except wikipedia.exceptions.PageError:
                await ctx.send("Pagina non esistente.")

    # todo definizione


def setup(client):
    client.add_cog(Google(client))
