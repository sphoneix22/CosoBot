import configparser
import gspread

import challonge
import discord
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials


cf = configparser.ConfigParser()
cf.read("'secret.ini")


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
                                  timestamp=(tourn['started-at']))
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

    @commands.command(name='stats_tornei')
    @commands.cooldown(1,60,commands.BucketType.user)
    async def stats_tornei(self,ctx):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('google_secret.json', scope)
        client = gspread.authorize(creds)
        sh = client.open('Tornei Brawlhalla').sheet1
        embed = discord.Embed(title='Classifica tornei Brawlhalla',
                              url='https://docs.google.com/spreadsheets/d/1q9Hr8qrAUVpdq5OyV1SF4b7n5C2j0QGQg-JXXSJ1B8s'
                                  '/edit?usp=sharing',
                              colour=discord.Colour(0x00ff07))
        embed.set_footer(text='Powered by Google Drive API',icon_url='http://icons.iconarchive.com/icons'
                                                                     '/marcus-roberto/google-play/128/Google-Drive-icon.png')
        partecipanti = ['Emacor','Sphoneix','Giobitonto','Peppe','Alessandro']
        for partecipante in partecipanti:
            cell = sh.find(partecipante)
            embed.add_field(name="**{}**".format(cell.value),value=f"Tornei vinti: {sh.cell(cell.row,2).value}",
                            inline=True)
        await ctx.send(embed=embed)



def setup(client):
    client.add_cog(Tournaments(bot=client))
