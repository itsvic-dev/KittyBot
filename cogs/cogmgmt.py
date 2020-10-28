import logging
import traceback

import discord
from discord.ext import commands

import api
from api import easystyle


class CogManagement(commands.Cog):
    def __init__(self, client):
        self.log = logging.getLogger(__name__)
        self.client = client

    @commands.is_owner()
    @commands.command()
    async def load(self, ctx, cog: str):
        try:
            self.client.load_extension(f"cogs.{cog}")
        except:
            embed = easystyle.embed(
                title=f"Failed to load `cogs.{cog}`!",
                description=f"```py\n{traceback.format_exc()}\n```",
                color=discord.Color.red()
            )
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            self.log.info(f"cogs.{cog} loaded by {str(ctx.author)}.")
            embed = easystyle.embed(
                title=f"Loaded `cogs.{cog}` successfully!",
                color=discord.Color.green()
            )
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.is_owner()
    @commands.command()
    async def unload(self, ctx, cog: str):
        try:
            self.client.unload_extension(f"cogs.{cog}")
        except commands.ExtensionAlreadyLoaded:
            pass
        except:
            embed = easystyle.embed(
                title=f"Failed to unload `cogs.{cog}`!",
                description=f"```py\n{traceback.format_exc()}\n```",
                color=discord.Color.red()
            )
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            self.log.info(f"cogs.{cog} unloaded by {str(ctx.author)}.")
            embed = easystyle.embed(
                title=f"Unloaded `cogs.{cog}` successfully!",
                color=discord.Color.green()
            )
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, cog: str):
        try:
            self.client.reload_extension(f"cogs.{cog}")
        except:
            embed = easystyle.embed(
                title=f"Failed to reload `cogs.{cog}`!",
                description=f"```py\n{traceback.format_exc()}\n```",
                color=discord.Color.red()
            )
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            self.log.info(f"cogs.{cog} reloaded by {str(ctx.author)}.")
            embed = easystyle.embed(
                title=f"Reloaded `cogs.{cog}` successfully!",
                color=discord.Color.green()
            )
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.is_owner()
    @commands.command()
    async def reloadAPI(self, ctx, specificAPI: str = None):
        embed = None
        try:
            import importlib
            if specificAPI is None:
                importlib.reload(api)
            elif specificAPI is "vars":
                importlib.reload(api.vars)
            elif specificAPI is "easystyle":
                importlib.reload(api.easystyle)
            elif specificAPI is "blacklist":
                importlib.reload(api.blacklist)
        except Exception:
            tb = traceback.format_exc()
            embed = easystyle.embed(
                title="Reloading APIs failed!",
                description=f"```py\n{tb}```",
                color=discord.Color.red()
            )
        else:
            embed = easystyle.embed(
                title="APIs have reloaded successfully!",
                description="You might need to reload cogs that import any of the APIs.",
                color=discord.Color.green()
            )
        finally:
            await ctx.send(ctx.author.mention, embed=embed)
            logging.info(f"{str(ctx.author)} reloaded APIs.")


def setup(client):
    client.add_cog(CogManagement(client))
