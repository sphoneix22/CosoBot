from discord.ext import commands

risposte = {
    'no': 'NO!',
    'silvio': 'PALDINO!',
    'altro che': 'IL FUTTBOOL, FUTTBOOOOL!!'
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
                           f"Qui c'è qualcuno che vuole parlare! {teodoro} {teodoro} {teodoro}")
        else:
            await ctx.send("Hey @everyone! Qui c'è qualcuno che vuole parlare!")

    async def on_message(self, ctx):
        if ctx.author.id != 457195507815546880:
            content = ctx.content.lower()
            try:
                await ctx.channel.send(risposte[content])
            except KeyError:
                return

    @commands.command(name='stop')
    @commands.has_role('CosoAdmin')
    async def stop(self, ctx):
        await ctx.send("Chiudendo il bot...")
        await self.client.logout()


def setup(client):
    client.add_cog(Chat(client))