import gc
import logging

from discord.ext import commands
import discord

import data
from api import blacklist, easystyle, vars
from api.cogloader import loadCogs

logformat = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=logformat)
log = logging.getLogger(__name__)

client = commands.AutoShardedBot(
    command_prefix=data.prefix,
    help_command=None,
    shard_count=data.shards,
    owner_ids=vars.botowners,
    activity=discord.Activity(type=discord.ActivityType.watching, name="Warming up..!")
)


@client.event
async def on_ready():
    loadCogs(client)
    log.info("Enabling Jishaku.")
    client.load_extension("jishaku")
    log.info("Enabling Python3 garbage collection.")
    gc.enable()
    httpCog = client.get_cog("HTTP")
    if httpCog is not None:
        log.info("Restarting the HTTP web server. (Commands page patch)")
        client.reload_extension("cogs.http")
    log.info("Ready!")


@client.event
async def on_message(message):
    if message.author.bot:
        return  # the message author is a bot, we don't want to process anything
    if blacklist.isInBlacklist(message.author.id):
        return  # the message author is blacklisted, we don't want to process anything
    await client.process_commands(message)


@client.event
async def on_command(ctx):
    channel = client.get_channel(746317661696163932)
    embed = easystyle.embed(
        title=f"{str(ctx.author)} ({str(ctx.author.id)}) used command in {ctx.guild.name} ({str(ctx.guild.id)})",
        description=ctx.message.content
    )
    if len(ctx.message.attachments) > 0:
        embed.set_image(url=ctx.message.attachments[0].url)
    embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
    await channel.send(embed=embed)


if __name__ == "__main__":
    client.run(data.token)
