import asyncio

import discord
from discord.ext import commands
import data
from api import vars


class Status(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.loop.create_task(self.background_set_status())
        self.name = f"{data.prefix}help"
        self.type = discord.ActivityType.listening

    async def background_set_status(self):
        while not self.client.is_closed():
            activity = discord.Activity(type=self.type, name=f"{self.name} | {str(len(self.client.guilds))} servers | "
                                                             f"{vars.domain}")
            await self.client.change_presence(activity=activity)
            await asyncio.sleep(10)


def setup(client):
    client.add_cog(Status(client))
