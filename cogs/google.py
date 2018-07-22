import asyncio
import os

import discord
import wikipedia
from discord.ext import commands
from google_images_download import google_images_download
from italian_dictionary import get_all_data, exceptions

response = google_images_download.googleimagesdownload()


class GID:
    """
    Google Image Downloader
    """
    @classmethod
    def downloader(cls, keyword):
        opts = {'keywords': keyword,
                'limit': 1,
                'output_directory': f"{os.getcwd()}/data/cache/images",
                'no_directory': True,
                'delay': 3,
                'extract-metadata': True,
                'format': 'jpg'}
        path = response.download(opts)
        return path


class Google:
    def __init__(self, client):
        self.client = client

    @commands.command('image')
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def image(self, ctx, query:str):
        """
        Downloads and image from google and sends it to user channel.
        -----------
        :param ctx: discord.ext.commands.Context
        :return: discord.client.message
        """
        async with ctx.typing():
            path = GID.downloader(query)
            actual_path = path[query][0]    #path returns a list of images with nested list
            return await ctx.send("**{}**".format(query), file=discord.File(actual_path))

    # todo text search

    @commands.command(name='wiki')
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def wiki(self, ctx, query:str):
        """
        Looks up on Wikipedia and sends embed.
        -----------------
        :param ctx: discord.ext.commands.Context
        :return: discord.Client.Message
        """
        wikipedia.set_lang('it')
        async with ctx.typing():
            def get_image(pg):
                try:
                    for img in pg.images:
                        if img[-3:] == 'jpg' or img[-3:] == 'png':  #if supported discord image
                            return str(img)
                except KeyError:
                    return None

            try:
                page = wikipedia.page(query)
                summary = wikipedia.summary(query, sentences=3)
                embed = discord.Embed(title=f"**{page.title}**", url=page.url, colour=discord.Colour(0x8f8f87),
                                      description=summary)

                image = get_image(page)

                if image is not None:
                    embed.set_thumbnail(url=image)
                embed.set_footer(text='Powered by Wikipedia API',
                                 icon_url='https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia'
                                          '-logo-v2.svg/1122px-Wikipedia-logo-v2.svg.png')
                return await ctx.send(embed=embed)
            except wikipedia.exceptions.DisambiguationError as e:
                # We are going to let the user choose some wikipedia sources, but if the name is the same it hasn't got
                # much sense
                actual_options = [x for x in e.options if x.lower() != query]
                if len(actual_options) == 0:
                    return await ctx.send(
                        f"Mi dispiace, ma non riesco ad individuare una pagina. Prova ad essere più specifico,"
                        f"{ctx.message.author.mention}")

                while len(actual_options) > 5:  #max size is 5
                    del actual_options[-1]

                embed = discord.Embed(title=f"Pagina di disambiguazione di **{query}**",
                                      colour=discord.Colour(0x8f8f87),
                                      description="Ci sono varie pagine che corrispondono a questa ricerca, scegli"
                                                  " quella che ti interessa.\nSe non la trovi prova di nuovo a cercare"
                                                  " in modo più specifico")

                for option in actual_options:
                    embed.add_field(name=option, value=f"**{actual_options.index(option)+1}**", inline=True)

                sent_msg = await ctx.send(embed=embed)

                emojis = {1: "\U00000031\U000020e3", 2: "\U00000032\U000020e3", 3: "\U00000033\U000020e3",
                          4: "\U00000034\U000020e3", 5: "\U00000035\U000020e3"}

                for index in range(1, len(actual_options) + 1): #let's add reaction
                    await sent_msg.add_reaction(emojis[index])

                def check(reaction, user):
                    return str(reaction.emoji) in emojis.values() and user == ctx.message.author \
                            and reaction.message.id == sent_msg.id

                try:
                    # wait for reaction
                    rct, usr = await self.client.wait_for("reaction_add", check=check, timeout=30)
                except asyncio.TimeoutError:
                    return await ctx.send("Tempo scaduto.")

                index = []

                for emoji in emojis.values():
                    if emoji == str(rct.emoji):
                        index = list(emojis.values()).index(emoji)  # match the choosen emoji to the list index

                page = wikipedia.page(actual_options[index])
                summary = wikipedia.summary(actual_options[index], sentences=3)

                new_embed = discord.Embed(title=f"**{page.title}**", url=page.url, colour=discord.Colour(0x8f8f87),
                                          description=summary)

                image = get_image(page)

                if image is not None:
                    embed.set_thumbnail(url=image)
                embed.set_footer(text='Powered by Wikipedia API',
                                 icon_url='https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg'
                                          '/1122px-Wikipedia-logo-v2.svg.png')
                return await ctx.send(embed=new_embed)

            except wikipedia.exceptions.PageError:
                return await ctx.send("Pagina non esistente.")

    @commands.command(name='def')
    async def dictionary(self, ctx, word:str):
        """
        Searches on dizionario-italiano.it and sends an embed.
        ------------
        :param ctx: discord.ext.commands.Context
        :return: discord.Client.Message
        """
        try:
            defs = get_all_data(word)
            embed = discord.Embed(title=defs['lemma'], url=defs['url'], description=defs['definizione'][0])
            embed.add_field(name="Grammatica", value=defs['grammatica'], inline=True)
            embed.add_field(name="Pronuncia", value=defs['pronuncia'], inline=True)
            embed.set_footer(text="Powered by italian_dictionary PP",
                             icon_url="https://us.123rf.com/450wm/paolo77/paolo771206/paolo77120600033/14002277"
                                      "-italian-flag-and-language-icon-isolated-vector-illustration.jpg")
            return await ctx.send(embed=embed)
        except exceptions.WordNotFoundError:
            return await ctx.send(f"Hey, {word} sembra non essere una parola esistente nel dizionario.")


def setup(client):
    client.add_cog(Google(client))
