import logging

from discord.ext import commands

from api import categories, easystyle, vars

log = logging.getLogger(__name__)


class HelpCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        categories.addToCategory("general", self)

    @commands.command(
        usage="k.help [category or command]",
        description="Lets you browse through categories and commands to find what you need."
    )
    async def help(self, ctx, *, argsStr: str = None):
        embed = easystyle.embed(
            title=f"{vars.botname} Help"
            # description = "PROTOTYPE | INTERNAL USE ONLY"
        )
        if argsStr is None:
            # show categories
            cts = categories.getCategories()
            ctsList = []
            for ctsKey, _ in cts.items():
                ctsList.append(f"`k.help {ctsKey}` » {categories.getCategoryDesc(ctsKey)}")
            embed.add_field(
                name="Categories",
                value="\n".join(sorted(ctsList))
            )
            del ctsList
            return await ctx.send(ctx.author.mention, embed=embed)
        else:
            args = argsStr.split(" ")
            requested = args[0]
            # determine if user requested category details or command help
            isCategory = False
            category = None
            command = None
            cts = categories.getCategories()
            for ctsKey, _ in cts.items():
                if requested == ctsKey:
                    isCategory = True
                    category = requested
                    break
            if isCategory:
                # show category cmds
                ctsCogs = categories.getCategoryCogs(category)
                cmds = {}
                for _, cog in ctsCogs.items():
                    for cmd in cog.get_commands():
                        if cmd.name.startswith("_"):
                            continue
                        cmds.update({cmd.name: cmd.description if cmd.description else 'None'})
                commandStrs = []
                for cmd in sorted(cmds.keys()):
                    commandStrs.append(f"`k.{cmd}` » {cmds[cmd]}")
                embed.add_field(
                    name=categories.getCategoryDesc(category),
                    value="\n".join(commandStrs)
                )
                return await ctx.send(ctx.author.mention, embed=embed)
            else:
                command = requested
                category = None
                foundCmd = None
                # find cog this command belongs to
                cts = categories.getCategories()
                for ctsCategory, ctsCogs in cts.items():
                    for _, cog in ctsCogs.items():
                        for cmd in cog.get_commands():
                            if cmd.name == command:
                                foundCmd = cmd
                                category = ctsCategory
                                break
                if foundCmd is None:
                    raise commands.UserInputError("Command not found.")
                else:
                    # display cmd info
                    embed.description = f"`k.{foundCmd.name}`"
                    if len(foundCmd.aliases) > 0:
                        aliases = [f"`{alias}`" for alias in foundCmd.aliases]
                        embed.add_field(
                            name="Aliases",
                            value="\n".join(aliases)
                        )
                    embed.add_field(
                        name="Description",
                        value=foundCmd.description if foundCmd.description else "None"
                    )
                    if foundCmd.usage is not None:
                        embed.add_field(
                            name="Usage",
                            value=f"`{foundCmd.usage}`"
                        )
                    return await ctx.send(ctx.author.mention, embed=embed)


def setup(client):
    client.add_cog(HelpCog(client))
