import asyncio
import functools
import logging
import platform
import subprocess
import time
import traceback

import discord
import psutil
import requests
from discord.ext import commands
from api import easystyle, blacklist

class Maintenance(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.counterData = []
        self.client.loop.create_task(self.background_check_counters())

    @commands.is_owner()
    @commands.command()
    async def blacklist(self, ctx, userid: int):
        if blacklist.isInBlacklist(userid):
            return await ctx.send("They're already blacklisted.")
        blacklist.addToBlacklist(userid)
        await ctx.send("Added to blacklist.")

    @commands.is_owner()
    @commands.command()
    async def unblacklist(self, ctx, userid: int):
        if not blacklist.isInBlacklist(userid):
            return await ctx.send("They're not blacklisted.")
        blacklist.removeFromBlacklist(userid)
        await ctx.send("Removed from blacklist.")
        pass

    @commands.is_owner()
    @commands.command()
    async def stop(self, ctx):
        await ctx.send("bye xdxd")
        logging.info(f"Shutdown started by {str(ctx.author)}")
        await self.client.logout()

    @commands.is_owner()
    @commands.command()
    async def say(self, ctx, *, msg):
        await ctx.message.delete()
        await ctx.send(msg)

    @commands.is_owner()
    @commands.command()
    async def bash(self, ctx, *, bashcmd):
        def force_async(fn):
            from concurrent.futures import ThreadPoolExecutor
            import asyncio
            pool = ThreadPoolExecutor()

            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                future = pool.submit(fn, *args, **kwargs)
                return asyncio.wrap_future(future)  # make it awaitable

            return wrapper

        @force_async
        def runCmd(cmd):
            return subprocess.check_output(['/bin/bash', '-c', cmd]).decode()

        output = await runCmd(bashcmd)
        await ctx.send("```\n" + output + "\n```")

    @commands.is_owner()
    @commands.command(name='eval')
    async def _eval(self, ctx, *, command):
        placeholder = "async def flexExec():\n{}"
        cmds = [f"  {cmd}" for cmd in command.replace("```py", "").replace("```", "").split("\n")]
        executeData = placeholder.format("\n".join(cmds))
        execGlobals = {
            "ctx": ctx,
            "client": self.client,
            "discord": discord,
            "commands": commands,
            "sellf": self
        }
        execLocals = {}
        try:
            exec(executeData, execGlobals, execLocals)
            ret = await execLocals['flexExec']()
        except Exception as e:
            embed = easystyle.embed(
                title=str(type(e).__name__),
                color=discord.Color.red()
            )
            tb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            embed.add_field(name="Traceback", value=f"```py\n{tb}\n```")
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = easystyle.embed(
                title="Success!",
                color=discord.Color.green()
            )
            embed.add_field(name="Result", value=f"```py\n{str(ret)}\n```")
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.is_owner()
    @commands.command()
    async def stats(self, ctx):
        embed = easystyle.embed(
            title="Statistics"
            # description=f"System statistics that Kitty is running on currently."
        )
        try:
            disk = subprocess.check_output(["df", "/", "--output=pcent"])
        except:
            disk = None
        embed.add_field(name="System", value=platform.system())
        embed.add_field(name="Python", value=platform.python_version())
        embed.add_field(name="Discord.py version", value=discord.__version__)
        embed.add_field(name="CPU usage", value=str(round(psutil.cpu_percent(), 1)) + "%")
        embed.add_field(name="Memory usage", value=str(round(psutil.virtual_memory().percent, 1)) + "%")
        embed.add_field(name="Disk usage", value=disk.decode().split("\n")[1] if disk is not None else "N/A")
        embed.add_field(name="Hostname", value=platform.node())
        chart = {
            'type': 'line',
            'data': {
                'labels': [i['timestamp'] for i in self.counterData],
                'datasets': [
                    {
                        'label': "CPU usage",
                        'data': [i['cpu'] for i in self.counterData],
                        'fill': False,
                        'borderColor': 'green'
                    },
                    {
                        'label': "RAM usage",
                        'data': [i['mem'] for i in self.counterData],
                        'fill': False,
                        'borderColor': 'blue'
                    }
                ]
            },
            'options': {
                'legend': {
                    'labels': {
                        'fontColor': 'white'
                    }
                }
            }
        }
        r = requests.post("https://quickchart.io/chart/create", json={"chart": chart})
        embed.set_image(url=r.json()['url'])
        await ctx.send(embed=embed)

    async def background_check_counters(self):
        while not self.client.is_closed():
            await asyncio.sleep(2)
            self.counterData.append({
                "cpu": round(psutil.cpu_percent(), 1),
                "mem": round(psutil.virtual_memory().percent, 1),
                "timestamp": time.time()
            })
            if len(self.counterData) > 60:
                del self.counterData[0]


def setup(client):
    client.add_cog(Maintenance(client))
