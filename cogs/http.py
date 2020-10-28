import discord
import jinja2
from discord.ext import commands
from aiohttp import web
from multiprocessing import Process
from api import vars, categories
import asyncio
import aiohttp_jinja2


def quote(thing: str):
    return thing.replace(":", "%3A").replace("/", "%2F")


class HTTP(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.process = Process(target=self.run_app, daemon=True)
        self.process.start()


    def run_app(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        app = self.get_app()
        web.run_app(
            app,
            host="127.0.0.1",
            port=5656,
            access_log=None
        )

    def get_app(self):
        app = web.Application()
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./html'))
        app.add_routes([
            web.static("/static/", "./static/"),
            web.get("/", self.index),
            web.get("/commands", self.commands),
            web.get('/added', self.added),
            web.get('/preview', self.preview)
        ])
        return app

    # ========== start routes here
    @aiohttp_jinja2.template("index.html")
    async def index(self, request):
        return {
            'linkNewPage': False,
            'support': vars.supportInvite,
            'invite': f"https://discord.com/api/oauth2/authorize?client_id={str(self.client.user.id)}"
                      "&permissions=8&scope=bot",
            'avatar': vars.avatar
        }

    @aiohttp_jinja2.template("index.html")
    async def preview(self, request):
        return {
            'linkNewPage': True,
            'support': vars.supportInvite,
            'invite': f"https://discord.com/api/oauth2/authorize?client_id={str(self.client.user.id)}"
                      "&permissions=8&scope=bot",
            'avatar': vars.avatar
        }

    @aiohttp_jinja2.template("added.html")
    async def added(self, request):
        return {}

    @aiohttp_jinja2.template("commands.html")
    async def commands(self, request):
        allC = categories.getCategories()
        categoriesExistent = []
        categoryData = {}
        for category, cogs in allC.items():
            categoriesExistent.append(category)
            if category not in categoryData:
                categoryData[category] = {
                    "description": categories.getCategoryDesc(category),
                    "commands": []
                }
            for cog in cogs:
                for cmd in self.client.get_cog(cog).get_commands():
                    categoryData[category]['commands'].append({
                        "name": cmd.name,
                        "description": cmd.description,
                        "aliases": cmd.aliases
                    })
            categoryData[category]['commands'].sort(key=lambda x: x['name'])
        return {'categories': sorted(categoriesExistent), 'categoryData': categoryData, 'avatar': vars.avatar}
    # ========== end routes here

    def cog_unload(self):
        self.process.kill()


def setup(client):
    client.add_cog(HTTP(client))
