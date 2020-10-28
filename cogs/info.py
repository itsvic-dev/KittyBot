from typing import Union

import discord
from discord.ext import commands

from api import categories, easystyle, vars


class InfoCmds(commands.Cog):
    def __init__(self, client):
        self.client = client
        categories.addToCategory("info", self)

    @commands.command(
        aliases=['pfp'],
        description="Shows your or other user's avatar.",
        usage="k.avatar [user]"
    )
    async def avatar(self, ctx, *, user: discord.User = None):
        if user is None:
            user = self.client.get_user(ctx.author.id)
        embed = easystyle.embed(title=f"{str(user)}'s avatar")
        embed.set_image(url=user.avatar_url)
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(
        description="Shows your or other user's details.",
        usage="k.userinfo [user]"
    )
    async def userinfo(self, ctx, *, user: Union[discord.User, int] = None):
        if isinstance(user, int):
            user = await self.client.fetch_user(user)
        if user is None:
            user = self.client.get_user(ctx.author.id)
        suffix = " (BOT)" if user.bot else ""
        embed = easystyle.embed(title=f"Details about {str(user)}{suffix}")
        embed.add_field(name="Created at", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        member: discord.Member = ctx.guild.get_member(user.id)
        if member is None:
            for guild in self.client.guilds:
                temp = guild.get_member(user.id)
                if temp is not None:
                    member = temp
                    break
        if member is not None:
            if isinstance(member.status, discord.Status):
                statusName = ""
                if member.status == discord.Status.dnd:
                    statusName = "Do Not Disturb"
                if member.status == discord.Status.online:
                    statusName = "Online"
                if member.status == discord.Status.idle:
                    statusName = "Idle"
                if member.status == discord.Status.offline:
                    statusName = "Offline"
                embed.add_field(name="Status", value=f"{vars.emojis[member.status.value]} {statusName}")
            for activity in member.activities:
                if activity is not None:
                    if activity.name is not None or activity.emoji is not None:
                        if isinstance(activity, discord.CustomActivity):
                            status = []
                            if activity.emoji is not None:
                                status.append(str(activity.emoji))
                            if activity.name is not None:
                                status.append(activity.name)
                            embed.add_field(name="Custom Activity", value=" ".join(status))
                        elif isinstance(activity, discord.Streaming):
                            embed.add_field(name=f"Streaming on {activity.platform}", value=f"[{activity.name}]"
                                                                                            f"({activity.url})")
                        elif isinstance(activity, discord.Spotify):
                            artists = ', '.join(activity.artists)
                            embed.add_field(name="Listening on Spotify", value=f"{artists} - {activity.title}")
                        elif isinstance(activity, discord.Game):
                            embed.add_field(name="Playing", value=activity.name)
                        elif isinstance(activity, discord.Activity):
                            if activity.type == discord.ActivityType.playing:
                                embed.add_field(name="Playing", value=activity.name)
                            elif activity.type == discord.ActivityType.streaming:
                                embed.add_field(name="Streaming", value=activity.name)
                            elif activity.type == discord.ActivityType.listening:
                                embed.add_field(name="Listening to", value=activity.name)
                            elif activity.type == discord.ActivityType.watching:
                                embed.add_field(name="Watching", value=activity.name)
            if member.guild.id == ctx.guild.id:
                if member.joined_at is not None:
                    embed.add_field(name="Joined at", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="ID", value=str(user.id))
        publicFlags = []

        if user.public_flags.hypesquad_balance:
            publicFlags.append("<:balance:737641844732592178> Hypesquad Balance")
        elif user.public_flags.hypesquad_bravery:
            publicFlags.append("<:bravery:737641275624521779> Hypesquad Bravery")
        elif user.public_flags.hypesquad_brilliance:
            publicFlags.append("<:brilliance:737641844661420112> Hypesquad Brilliance")
        if user.public_flags.staff:
            publicFlags.append("<:staff:737642960568582194> Discord Staff")
        if user.public_flags.partner:
            publicFlags.append("<:partner:737642666573168710> Discord Partner")
        if user.public_flags.hypesquad:
            publicFlags.append("<:hypesquad:737645193838329876> Hypesquad Events")
        if user.public_flags.bug_hunter:
            publicFlags.append("<:bughunter:737643281789354045> Bug Hunger")
        if user.public_flags.verified_bot:
            publicFlags.append("<:verifiedBot:737647956261601331> Verified Bot")
        if user.public_flags.verified_bot_developer:
            publicFlags.append("<:verifiedDev:737645193406185503> Verified Bot Developer")
        if len(publicFlags) != 0:
            embed.add_field(name="Badges", value="\n".join(publicFlags))
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(
        aliases=['guildinfo'],
        description="Shows this server or other server's details.",
        usage="k.serverinfo [server]"
    )
    async def serverinfo(self, ctx, *, guild: discord.Guild = None):
        if guild is None:
            guild = ctx.guild
        if guild.unavailable:
            raise commands.CheckFailure("Server is unavailable at this time. Sorry!")
        embed = easystyle.embed(title=f"Details about {guild.name}")
        embed.add_field(name="Created at", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        member = ctx.guild.get_member(ctx.author.id)
        if member is not None:
            if member.joined_at is not None:
                embed.add_field(name="You joined at", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="ID", value=str(guild.id))
        embed.add_field(name="Owner", value=str(guild.owner))
        embed.add_field(name="Region", value=str(guild.region))
        if guild.afk_timeout != 0 and guild.afk_channel is not None:
            embed.add_field(name="Voice AFK timeout", value=str(guild.afk_timeout))
        embed.add_field(name="Member count", value=str(guild.member_count))
        embed.add_field(name="Server boosters", value=str(guild.premium_subscription_count))
        embed.add_field(name="Nitro Boost level", value=str(guild.premium_tier))
        embed.add_field(name="Do moderators require 2FA?", value="Yes" if guild.mfa_level == 1 else "No")
        embed.set_thumbnail(url=guild.icon_url)
        if guild.banner is not None:
            embed.set_image(url=guild.banner_url)
        await ctx.send(ctx.author.mention, embed=embed)


def setup(client):
    client.add_cog(InfoCmds(client))
