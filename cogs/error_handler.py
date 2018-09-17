from discord.ext import commands
import youtube_dl

class CommandErrorHandler:
    def __init__(self, client):
        self.client = client

    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.errors.DisabledCommand):
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
                await ctx.send("C'è stato un errore nel download. Non posso farci nulla.")


def setup(client):
    client.add_cog(CommandErrorHandler(client))
