import asyncio
import time
from datetime import datetime
from subprocess import call
import discord
from discord.ext import commands
from random import choice

risposte = {
    'silvio': 'PALDINO!',
    'altro che': 'IL FUTTBOOL, FUTTBOOOOL!!',
    'obunga': 'AARGHHH!!',
    'acribisignanoluzzi': 'tu puzzi',
    'pino': 'il veneziano',
    'peppe': 'compra la ps4',
    'gerardo': '...Paldino, conosciuto anche come re di Luzzi, '
               'nonchè governatore supremo e protettore della Terra '
               'tramite le forze armate, è una rispettabilissima persona degna di tale riconoscimenti.',
    'sphoneix': 'Esperto di fantaciclismo',
    'good bot': 'Grazie!',
    'bravo': 'Grazie!'
}

risposte_singole = {
    'no':"NO!"
}

class Chat():
    def __init__(self, client):
        self.client = client

    @commands.command(name='teodoro',
                      description='Sveglia le persone sul server',
                      brief='TEODORO!')
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def teodoro(self, ctx):
        teodoro = '<:teodoroemoji2:403218863967174667>'
        guild = str(ctx.message.guild)
        await ctx.message.delete()
        if guild == 'Serverino bellino & Bananen':
            await ctx.send(f" {teodoro} {teodoro} {teodoro} Hey @everyone! "
                           f"{ctx.message.author.mention} vuole parlare! {teodoro} {teodoro} {teodoro}")
        else:
            await ctx.send(f"Hey @everyone! {ctx.message.author.mention} vuole parlare!")

    async def on_message(self, ctx):
        if ctx.author.id != 457195507815546880:
            content = ctx.content.lower()
            try:
                if content in risposte_singole.keys():
                    await ctx.delete()
                    return await ctx.channel.send(risposte_singole[content])
                return await ctx.channel.send(risposte[content])
            except KeyError:
                return
        return

    @commands.command(name='chiudi')
    async def stop(self, ctx):
        if await self.client.is_owner(ctx.author):
            await ctx.send("Chiudendo il bot...")
            await self.client.logout()
        else:
            await ctx.send('Ma chi ti credi di essere? Non sei mica il mio padrone!')

    @commands.command(name='github')
    async def github(self, ctx):
        await ctx.send(f"Tieni, {ctx.message.author.mention}. \n "
                       f"https://github.com/sphoneix22/CosoBot")

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        elaps = time.time() - self.client.start_time
        minute, second = divmod(elaps, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)
        embed = discord.Embed(title='Bot attivo da:', description="{} giorni, "
                                                                  "{} ore, "
                                                                  "{} minuti, "
                                                                  "{} secondi".format(int(day),
                                                                                      int(hour),
                                                                                      int(minute),
                                                                                      int(second)),
                              timestamp=datetime.utcfromtimestamp(self.client.start_time))
        embed.set_footer(text='Last time started:', icon_url='https://png.icons8.com/color/1600/raspberry-pi.png')
        await ctx.send(embed=embed)

    @commands.command(name='reboot')
    @commands.is_owner()
    async def reboot(self,ctx):
        if self.client.linux is True:
            msg = await ctx.send("Questo comando riavvierà il Raspberry Pi! Sei sicuro?")
            await msg.add_reaction('👍')
            author = ctx.message.author
            def check(reaction, user):
                return user == author and str(reaction.emoji) == '👍' and reaction.message.id == msg.id
            try:
                await self.client.wait_for('reaction_add',timeout=60,check=check)
                await ctx.send("Ok, riavviando...")
                call('reboot')
            except asyncio.TimeoutError:
                await ctx.send("Ok, non lo riavvio.")
        else:
            await ctx.send("Il bot si trova in ambiente Windows, non posso riavviarlo.")

    @commands.command(name='moneta')
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def moneta_(self, ctx):
        ch = ["testa", "croce"]
        await ctx.send(f"E' uscita {choice(ch)}, {ctx.message.author.mention}")

    @commands.command(name='scegli')
    async def scegli_(self, ctx, param1:str,param2:str):
        if param1.lower() == param2.lower():
            return await ctx.send("Ah! Ti sarebbe piaciuto fregarmi, {}!".format(ctx.message.author.mention))
        msg = ["Sinceramente prefisco **{}**.", "In tutta franchezza, **{}** è meglio.", "Ma che domanda è? Ovviamente preferisco"
                                                                                 " **{}**!"]
        await ctx.send(choice(msg).format(choice([param1,param2])))

    @commands.command(name='ping')
    async def ping_(self, ctx):
        await ctx.send("PONG!")

def setup(client):
    client.add_cog(Chat(client))
