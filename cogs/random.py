import discord
from discord.ext import commands
from api import easystyle
import aiohttp


class Random(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @staticmethod
    async def getRandomNumber(start: int, end: int):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.random.org/integers/?num=1&min={str(start)}&max={str(end)}"
                                   "&col=1&base=10&format=plain&rnd=new") as resp:
                return int(await resp.text())

    @commands.command(
        description="Gives you a random number."
    )
    async def rng(self, ctx: commands.Context, start: int = 1000, end: int = None):
        if end is None:
            end = start
            start = 1
        if start > end:
            raise commands.UserInputError("The start number cannot be higher than the end number.")
        number = await self.getRandomNumber(start, end)
        embed = easystyle.embed(
            title="Here's your random number!",
            description=f"`{str(number)}`"
        )
        await ctx.send(ctx.author.mention, embed=embed)


def setup(client):
    client.add_cog(Random(client))
