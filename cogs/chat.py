from discord.ext import commands
risposte = {
    'no': 'NO!',
    'silvio': 'PALDINO!',
    'altro che': 'IL FUTTBOOL, FUTTBOOOOL!!',
    'obunga': 'AARGHHH!!',
    'acribisignanoluzzi': 'tu puzzi',
    'pino': 'il veneziano',
    'peppe': 'compra la ps4',
    'gerardo': '...Paldino, conosciuto anche come re di Luzzi, '
               'nonchè governatore supremo e protettore della Terra '
               'tramite le forze armate, è una rispettabilissima persona degna di tale riconoscimenti.',
    'sphoneix': 'Esperto di fantaciclismo'
}

class Chat():
    def __init__(self, client):
        self.client = client

    @commands.command(name='teodoro',
                      description='Sveglia le persone sul server',
                      brief='TEODORO!')
    @commands.cooldown(1, 120, commands.BucketType.guild)
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
                await ctx.channel.send(risposte[content])
            except KeyError:
                return

    @commands.command(name='stop')
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


def setup(client):
    client.add_cog(Chat(client))
