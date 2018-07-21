import asyncio
import os

import discord
from discord.ext import commands
from google_images_download import google_images_download
from italian_dictionary import get_all_data, exceptions

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
        self.client = client

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
            def get_image(page):
                try:
                    for image in page.images:
                        if image[-3:] == 'jpg' or image[-3:] == 'png':
                            return str(image)
                except:
                    return None

            try:
                page = wikipedia.page(query)
                sum = wikipedia.summary(query,sentences=3)
                embed = discord.Embed(title=f"**{page.title}**",url=page.url,colour=discord.Colour(0x8f8f87),
                                      description=sum)

                image = get_image(page)

                if image is not None:
                    embed.set_thumbnail(url=image)
                embed.set_footer(text='Powered by Wikipedia API',
                                 icon_url='https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/1122px-Wikipedia-logo-v2.svg.png')
                await ctx.send(embed=embed)
            except wikipedia.exceptions.DisambiguationError as e:
                actual_options = [x for x in e.options if x.lower() != query]

                if len(actual_options) == 0:
                    return await ctx.send(f"Mi dispiace, ma non riesco ad individuare una pagina. Prova ad essere più specifico,"
                                          f"{ctx.message.author.mention}")

                while len(actual_options)>5:
                    del actual_options[-1]

                embed = discord.Embed(title=f"Pagina di disambiguazione di **{query}**",colour=discord.Colour(0x8f8f87),
                                      description="Ci sono varie pagine che corrispondono a questa ricerca, scegli"
                                                  " quella che ti interessa.\nSe non la trovi prova di nuovo a cercare"
                                                  " in modo più specifico")

                for option in actual_options:
                    embed.add_field(name=option,value=f"**{actual_options.index(option)+1}**",inline=True)


                sent_msg = await ctx.send(embed=embed)

                emojis = {1:"\U00000031\U000020e3", 2: "\U00000032\U000020e3", 3:"\U00000033\U000020e3",
                          4: "\U00000034\U000020e3", 5:"\U00000035\U000020e3"}

                for index in range(1,len(actual_options)+1):
                    await sent_msg.add_reaction(emojis[index])

                def check(reaction,user):
                    return str(reaction.emoji) in emojis.values() and user == ctx.message.author and reaction.message.id == sent_msg.id

                try:
                    reaction, user = await self.client.wait_for("reaction_add", check=check,timeout=30)
                except asyncio.TimeoutError:
                    return await ctx.send("Tempo scaduto.")

                for emoji in emojis.values():
                    if emoji == str(reaction.emoji):
                        index = list(emojis.values()).index(emoji)

                page = wikipedia.page(actual_options[index])
                sum = wikipedia.summary(actual_options[index], sentences=3)

                new_embed = discord.Embed(title=f"**{page.title}**", url=page.url, colour=discord.Colour(0x8f8f87),
                                      description=sum)

                image = get_image(page)

                if image is not None:
                    embed.set_thumbnail(url=image)
                embed.set_footer(text='Powered by Wikipedia API',
                                 icon_url='https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/1122px-Wikipedia-logo-v2.svg.png')
                await ctx.send(embed=new_embed)

            except wikipedia.exceptions.PageError:
                await ctx.send("Pagina non esistente.")

    @commands.command(name='def')
    async def dictionary(self,ctx):
        word = ctx.message.content[5:]
        try:
            defs = get_all_data(word)
            embed = discord.Embed(title=defs['lemma'], url=defs['url'], description=defs['definizione'][0])
            embed.add_field(name="Grammatica", value=defs['grammatica'], inline=True)
            embed.add_field(name="Pronuncia", value=defs['pronuncia'], inline=True)
            embed.set_footer(text="Powered by italian_dictionary PP",
                             icon_url="https://us.123rf.com/450wm/paolo77/paolo771206/paolo77120600033/14002277"
                                      "-italian-flag-and-language-icon-isolated-vector-illustration.jpg")
            await ctx.send(embed=embed)
        except exceptions.WordNotFoundError:
            await ctx.send(f"Hey, {word} sembra non essere una parola esistente nel dizionario.")


def setup(client):
    client.add_cog(Google(client))
