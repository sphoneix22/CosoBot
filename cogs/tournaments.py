import configparser
import datetime

import challonge
import discord
from discord.ext import commands

cf = configparser.ConfigParser()
cf.read('secret.ini')


class Tournaments():
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='challonge')
    async def chall(self, ctx):
        challonge.set_credentials('bananaglassata', cf.get(section='secret', option='challonge_api'))

    @chall.command(name='partecipanti')
    async def part(self, ctx):
        async with ctx.typing():
            torneo = ctx.message.content[24:]
            tourn = challonge.tournaments.show(torneo)
            part = challonge.participants.index(torneo)
            embed = discord.Embed(title=f"Partecipanti del torneo '{tourn['name']}' di {tourn['game-name']}",
                                  colour=discord.Colour(48942), url=tourn['full-challonge-url'],
                                  timestamp=datetime.datetime.utcfromtimestamp(1529600734))
            embed.set_thumbnail(
                url="https://challonge.com/assets/og-default-9d2c9e67cc219b24e19785afa8d289899116d96512f6096e67f04b854b2d174e.png")
            embed.set_footer(text="Powered by Challonge API",
                             icon_url="https://media.discordapp.net/attachments/258624439933992961/458288479864881152/COSOBOT.png")
            for player in part:
                if player['final-rank'] is None:
                    embed.add_field(name=f"**{player['name']}**", value="Posizione: Il torneo non è ancora terminato!",
                                    inline=True)
                else:
                    embed.add_field(name=f"**{player['name']}**", value=f"Posizione finale: {player['final-rank']}",
                                    inline=True)
        await ctx.channel.send(content=f"Ecco, {ctx.author.mention}", embed=embed)


def setup(client):
    client.add_cog(Tournaments(bot=client))
