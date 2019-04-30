from discord.ext import commands
import youtube_dl

class CommandErrorHandler(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.errors.DisabledCommand):
            if ctx.command.qualified_name == 'rl_rank' or ctx.command.qualified_name == 'rl_stats':
                return await ctx.send("L'API a cui si appoggiavano questi comandi non è più funzionante.\nPiù informazioni qui:"
                               " ``https://www.redd.it/97p7oh``\nAl momento non esiste un'alternativa ma potrebbe esserci in"
                               " futuro.")
            return await ctx.send(f'{ctx.command} è stato disabilitato')
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} non può essere utilizzato nei messagi privati.')
            except:
                pass
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.send(f"Calmati! {ctx.message.author.mention}")
            return await ctx.message.delete()
        elif isinstance(error,youtube_dl.DownloadError):
            if ctx.command.qualified_name == 'play':
                await ctx.send("C'è stato un errore nel download. Per favore segnalalo, è probabilmente un problema del pacchetto di download.")


def setup(client):
    client.add_cog(CommandErrorHandler(client))
