import asyncio
import time
from datetime import datetime
from subprocess import call
import discord
from discord.ext import commands
from random import choice
import requests
import json

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
    'no': "NO!"
}


class Chat(commands.Cog):
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

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.id != 457195507815546880: #todo remove this
            content = ctx.content.lower()
            try:
                if content in risposte_singole.keys():
                    await ctx.delete()
                    return await ctx.channel.send(risposte_singole[content])
                return await ctx.channel.send(risposte[content])
            except KeyError:
                return
        return

    @commands.command(name="disabilita")
    async def disable(self, ctx, query_command:str):
        if str(ctx.author.id) != self.client.config['owner_id']:
            return await ctx.send("Non sei autorizzato.")

        command = self.client.get_command(query_command)

        if command:
            command.enabled = False
            if not query_command in self.client.disabled_commands:
                self.client.disabled_commands.append(query_command)
                self.client.parser['commands']['disabled'] = json.dumps(self.client.disabled_commands)
                with open('secret.ini', 'w+') as configfile:
                    self.client.parser.write(configfile)

            return await ctx.send(f"Ho disabilitato il comando ``{query_command}``.")
        else:
            return await ctx.send(f"Il comando ``{query_command}`` non esiste.")

    @commands.command(name='comandi')
    async def see_commands(self, ctx):
        if len(self.client.disabled_commands) == 0:
            return await ctx.send("Tutti i comandi sono abilitati.")

        msg = "I seguenti comandi sono disabilitati:\n"
        for command in self.client.disabled_commands:
            msg += f"``{command}``\n"
        return await ctx.send(msg)

    @commands.command(name='abilita')
    async def activate_commands(self, ctx, query_command:str):
        if str(ctx.message.author.id) != self.client.config['owner_id']:
            return await ctx.send("Non sei autorizzato.")

        command = self.client.get_command(query_command)

        if command:
            if not command.enabled:
                command.enabled = True
                self.client.disabled_commands.remove(query_command)
                self.client.parser['commands']['disabled'] = json.dumps(self.client.disabled_commands)
                with open('secret.ini', 'w+') as configfile:
                    self.client.parser.write(configfile)
            return await ctx.send(f"Ho abilitato il comando ``{query_command}``.")
        else:
            await ctx.send(f"Il comando ``{query_command}`` non esiste.")


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
    async def reboot(self, ctx):
        if self.client.linux is True:
            msg = await ctx.send("Questo comando riavvierà il Raspberry Pi! Sei sicuro?")
            await msg.add_reaction('👍')
            author = ctx.message.author

            def check(reaction, user):
                return user == author and str(reaction.emoji) == '👍' and reaction.message.id == msg.id

            try:
                await self.client.wait_for('reaction_add', timeout=60, check=check)
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
    async def scegli_(self, ctx, param1: str, param2: str):
        if param1.lower() == param2.lower():
            return await ctx.send("Ah! Ti sarebbe piaciuto fregarmi, {}!".format(ctx.message.author.mention))
        msg = ["Sinceramente prefisco **{}**.", "In tutta franchezza, **{}** è meglio.",
               "Ma che domanda è? Ovviamente preferisco"
               " **{}**!"]
        await ctx.send(choice(msg).format(choice([param1, param2])))

    @commands.command(name='ping')
    async def ping_(self, ctx):
        await ctx.send("PONG!")

    @commands.command(name='server')
    async def server_(self, ctx):
        API = "https://api.minetools.eu/{}/{}"
        ping = requests.get(API.format("ping", self.client.config['minecraft_server'])).json()

        if "error" in ping:
            msg = await ctx.send("Il server non è attivo. Aggiungendo un'emoticon invierò un messaggio a Sphoneix.")
            await msg.add_reaction("📧")
            original_message = ctx.message

            def check(reaction, user):
                return str(reaction.emoji) == "📧" and user == original_message.author and reaction.message.id == msg.id

            try:
                r, u = await self.client.wait_for('reaction_add', timeout=60, check=check)
            except asyncio.TimeoutError:
                return
            else:
                await ctx.send("Ok, ora gli scrivo!")
                return await self.client.get_user(int(self.client.config['owner_id'])).send(
                    f"Hey! {str(ctx.message.author)} ha richiesto l'apertura del server di Minecraft.")

        query = requests.get(API.format("query", self.client.config['minecraft_server'])).json()

        if query['Players'] == 0:
            players_str = ''
        else:
            players_str = '|'
            for player in query['Playerlist']:
                if query['Playerlist'].index(player) == len(query['Playerlist']) - 1:
                    players_str += ' ' + player
                else:
                    players_str += f" {player},"

        embed = discord.Embed(title="Il server è attivo", description=ping['description'])
        embed.add_field(name="Giocatori online", value=f"{query['Players']}/{ping['players']['max']} {players_str}")
        embed.set_footer(text=f'Latency {str(ping["latency"])} ms',
                         icon_url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/i/977e8c4f-1c99-46cd-b070-10cd97086c08/d36qrs5-017c3744-8c94-4d47-9633-d85b991bf2f7.png")

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Chat(client))
