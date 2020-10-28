from typing import Union

import discord
from discord.ext import commands

from api import easystyle, config, categories


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        categories.addToCategory("mod", self)

    @commands.command(
        description="Kicks a member from the server.",
        usage="k.kick <member>"
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "None"):
        if member.id == ctx.author.id:
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                    title="You can't do that!",
                    description="I'm not going to kick you, dummy...",
                    color=discord.Color.red()
                )
            )
        try:
            await member.kick(reason=f"{str(ctx.author)} | {reason}")
        except discord.errors.Forbidden:
            raise commands.BotMissingPermissions(
                f"{str(member)} is either equal or higher than me in the roles. If this is unexpected, you will need "
                f"to fix your role positions.")
        else:
            embed = easystyle.embed(
                title=f"Kicked {str(member)} successfully!"
            )
            embed.add_field(name="Moderator", value=str(ctx.author))
            embed.add_field(name="Reason", value=reason)
            return await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(
        description="Bans a member from the server.",
        usage="k.ban <member>"
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: Union[discord.User, int], *, reason: str = "None"):
        if isinstance(member, int):
            member = await self.client.fetch_user(member)
        if member.id == ctx.author.id:
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                    title="You can't do that!",
                    description="I'm not going to ban you, dummy...",
                    color=discord.Color.red()
                )
            )
        try:
            await ctx.guild.ban(member, reason=f"{str(ctx.author)} | {reason}")
        except discord.errors.Forbidden:
            raise commands.CheckFailure(
                message=f"{str(member)} is either equal or higher than me in the roles. If this is unexpected, "
                        f"you will need to fix your role arrangement in Server Settings.")
        else:
            embed = easystyle.embed(
                title=f"Banned {str(member)} successfully!"
            )
            embed.add_field(name="Moderator", value=str(ctx.author))
            embed.add_field(name="Reason", value=reason)
            return await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(
        description="Warns a member in the server.",
        usage="k.warn <member> [reason]"
    )
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "None"):
        if member.id == ctx.author.id:
            return await ctx.send(ctx.author.mention, embed=easystyle.embed(
                    title="You can't do that!",
                    description="I'm not going to warn you, dummy...",
                    color=discord.Color.red()
                )
            )
        warnData = {
            "reason": reason,
            "moderatorID": str(ctx.author.id)
        }
        data = config.get("warnings", str(ctx.guild.id))
        if data is None:
            data = {str(member.id): [warnData]}
        else:
            if data.get(str(member.id)) is None:
                data.update({str(member.id): []})
            data.append(warnData)
        config.set("warnings", str(ctx.guild.id), data)
        embed = easystyle.embed(title=f"{str(member)} has been warned.", color=discord.Color.green())
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="Moderator", value=str(ctx.author))
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(
        description="Displays your or other member's warnings.",
        usage="k.warnings [member]"
    )
    async def warnings(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        else:
            if ctx.author.permissions_in(ctx.channel).kick_members is False:
                raise commands.MissingPermissions(["KICK_MEMBERS"])
        data = config.get("warnings", f"{str(ctx.guild.id)}.{str(member.id)}")
        readableWarnings = []
        for warnID in range(len(data)):
            warnData = data[warnID]
            readableWarnings.append(
                f"{str(warnID)} » {warnData['reason']} (by {str(self.client.get_user(int(warnData['moderatorID'])))})")
        embed = easystyle.embed(title=f"{str(member)}'s warnings", description="\n".join(readableWarnings))
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(
        description="Revokes a warning by its ID from a member.",
        usage="k.revokeWarn <member> <warning ID>"
    )
    @commands.has_permissions(kick_members=True)
    async def revokeWarn(self, ctx, member: discord.Member, warnID: int):
        data = config.get("warnings", f"{str(ctx.guild.id)}.{str(member.id)}")
        if warnID > len(data):
            raise commands.UserInputError(f"Warning {str(warnID)} does not exist.")
        warnData = data[warnID].copy()
        data.pop(warnID)
        config.set("warnings", f"{str(ctx.guild.id)}.{str(member.id)}", data)
        embed = easystyle.embed(title=f"Warning revoked", color=discord.Color.green())
        embed.add_field(name="Original reason", value=warnData['reason'])
        embed.add_field(name="Moderator", value=str(self.client.get_user(int(warnData['moderatorID']))))
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(
        description="Verify that you are a member.",
        usage="k.verify"
    )
    async def verify(self, ctx):
        data = config.get("verification", ctx.guild.id)
        if data is not None:
            for role in ctx.guild.roles:
                if role.id == data[1]:
                    await ctx.message.author.add_roles(role)
                    await ctx.message.delete()

    @commands.command(
        description="Setups verification process.",
        usage="k.verifySetup <channel> <role>"
    )
    @commands.has_permissions(manage_roles=True)
    async def verifySetup(self, ctx, channel: discord.TextChannel, role: discord.Role):
        data = config.get("verification", ctx.guild.id)
        if data is not None:
            raise commands.UserInputError(f"You have already setup verification!")

        config.set("verification", ctx.guild.id, [channel.id, role.id])

        embed = easystyle.embed(title=f"Done!", color=discord.Color.green())
        embed.add_field(name="New verify channel", value=f"#{channel.name}")
        embed.add_field(name="New verified role", value=role.name)

        verifyEmbed = easystyle.embed(
            title=f"Welcome to {str(ctx.guild)}!",
            color=discord.Color.green(),
            description="Send `k.verify` here to get a role!"
        )
        await ctx.send(ctx.author.mention, embed=embed)
        await channel.send(embed=verifyEmbed)


def setup(client):
    client.add_cog(Moderation(client))
