import io
import traceback
import discord
from discord.ext import commands
from api import easystyle
import aiohttp.client_exceptions


class CommandExceptionHandler(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)
        ignored = (commands.CommandNotFound, commands.NotOwner)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                title="Hold up!",
                description="You're not allowed to use this command, sorry!",
                color=discord.Color.red()
            ))

        if isinstance(error, commands.NSFWChannelRequired):
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                title="Hold up!",
                description="This command can be used **only** in NSFW channels or DMs, sorry!",
                color=discord.Color.red()
            ))

        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                title="Hold up!",
                description=f"This command is on cooldown! Please wait {str(round(error.retry_after, 1))} seconds "
                            f"before retrying.",
                color=discord.Color.red()
            ))

        if isinstance(error, commands.BotMissingPermissions):
            permslist = '\n - '.join(error.missing_perms)
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                title="Hold up!",
                description=f"The bot is missing the following permissions: {permslist}\nPlease make sure the bot "
                            f"either has the Administrator permission or the permissions listed above.",
                color=discord.Color.red()
            ))

        if isinstance(error, commands.CheckFailure):
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                title="Hold up!",
                description=f"One of our checks seem to have failed.\nHere's some more info: {error.message}",
                color=discord.Color.red()
            ))

        if isinstance(error, commands.UserInputError):
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                title="Hold up!",
                description=f"I think you're missing some arguments! If you need help, remember you can use the "
                            f"`k.help` command to quickly check what command does what!\nHere's some more info: "
                            f"{str(error)}",
                color=discord.Color.red()
            ))

        if isinstance(error, aiohttp.client_exceptions.InvalidURL):
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                title="Hold up!",
                description="It looks like you've entered an incorrect URL! Make sure the URL is correct, then try "
                            "again!",
                color=discord.Color.red()
            ))

        if isinstance(error, aiohttp.client_exceptions.ClientPayloadError):
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                title="Oops!",
                description="The server didn't send all the data properly!\nHere's some more info: "
                            f"{str(error)}",
                color=discord.Color.red()
            ))

        if isinstance(error, discord.NotFound):
            errorText = ""
            if error.text:
                errorText = f"\nHere's some more info: {error.text}"
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                title="Oops!",
                description=f"We couldn't find what you asked for!{errorText}"
            ))

        await ctx.send(ctx.author.mention, embed=easystyle.embed(
            title="Oops!",
            description="We're terribly sorry, but we've encountered an unexpected error!\nWe're sending the error "
                        "log to one of our developers, don't worry!",
            color=discord.Color.red()
        ))

        tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        msg = f"<@&701031325615915078>\n```py\n{tb}\n```"
        tracebackhell = self.client.get_channel(725880924788490281)
        if len(msg) > 2000:
            await tracebackhell.send("<@&701031325615915078> Here's the latest traceback!",
                                     file=discord.File(io.BytesIO(tb.encode())))
        else:
            await tracebackhell.send(msg)


def setup(client):
    client.add_cog(CommandExceptionHandler(client))
