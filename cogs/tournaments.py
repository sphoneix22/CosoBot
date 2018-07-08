import configparser

import challonge
import discord
import gspread
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials

cf = configparser.ConfigParser()
cf.read("'secret.ini")

partecipanti = ['Emacor', 'Sphoneix', 'Giobitonto', 'Peppe', 'Alessandro']


class Gsheets():
    @classmethod
    def start(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('google_secret.json', scope)
        return gspread.authorize(creds)


class Tournaments():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tornei')
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def tornei(self, ctx):
        client = Gsheets.start()
        sh = client.open('Tornei Brawlhalla').sheet1
        embed = discord.Embed(title='Classifica tornei Brawlhalla',
                              url='https://docs.google.com/spreadsheets/d/1q9Hr8qrAUVpdq5OyV1SF4b7n5C2j0QGQg-JXXSJ1B8s'
                                  '/edit?usp=sharing',
                              colour=discord.Colour(0x00ff07))
        embed.set_footer(text='Powered by Google Drive API', icon_url='http://icons.iconarchive.com/icons'
                                                                      '/marcus-roberto/google-play/128/Google-Drive-icon.png')
        for partecipante in partecipanti:
            cell = sh.find(partecipante)
            embed.add_field(name="**{}**".format(cell.value), value=f"Tornei vinti: {sh.cell(cell.row,2).value}",
                            inline=True)
        await ctx.send(embed=embed)

    @commands.command(name='tornei_add')
    @commands.is_owner()
    async def add_tourn(self, ctx):
        client = Gsheets.start()
        if ctx.message.content[12:] not in partecipanti:
            await ctx.send("Hey, ma se non mi dici chi ha vinto sei stupido.")
        else:
            sh = client.open("Tornei Brawlhalla").sheet1
            cell = sh.find(ctx.message.content[12:])
            value = int(sh.cell(cell.row, 2).value)
            sh.update_cell(cell.row, 2, value + 1)
            await ctx.send("Fatto! Congratulazioni a {}".format(ctx.message.content[12:]))


def setup(client):
    client.add_cog(Tournaments(bot=client))
