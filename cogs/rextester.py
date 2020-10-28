import aiohttp
import discord
from discord.ext import commands

from api import easystyle, categories

languages = {
    "c#": 1,
    "vb.net": 2,
    "f#": 3,
    "java": 4,
    "py2": 5,
    "c": 6,
    "c++": 7,
    "php": 8,
    "pascal": 9,
    "objective-c": 10,
    "haskell": 11,
    "ruby": 12,
    "perl": 13,
    "lua": 14,
    "nasm": 15,
    "sql-server": 16,
    "js": 17,
    "lisp": 18,
    "prolog": 19,
    "go": 20,
    "scala": 21,
    "scheme": 22,
    "node.js": 23,
    "py3": 24,
    "py": 24,
    "octave": 25,
    "d": 30,
    "r": 31,
    "tcl": 32,
    "mysql": 33,
    "postgresql": 34,
    "oracle": 35,
    "swift": 37,
    "bash": 38,
    "ada": 39,
    "erlang": 40,
    "elixir": 41,
    "ocaml": 42,
    "kotlin": 43,
    "brainfuck": 44,
    "fortran": 45,
    "rust": 46,
    "clojure": 47
}

compiler_args = {
    "c++": "-Wall -std=c++14 -O2 -o a.out source_file.cpp",
    "c": "-Wall -std=gnu99 -O2 -o a.out source_file.c",
    "d": "source_file.d -ofa.out",
    "go": "-o a.out source_file.go",
    "haskell": "-o a.out source_file.hs",
    "objective-c": "-MMD -MP -DGNUSTEP -DGNUSTEP_BASE_LIBRARY=1 -DGNU_GUI_LIBRARY=1 -DGNU_RUNTIME=1 -DGNUSTEP_BASE_LIBRARY=1 -fno-strict-aliasing -fexceptions -fobjc-exceptions -D_NATIVE_OBJC_EXCEPTIONS -pthread -fPIC -Wall -DGSWARN -DGSDIAGNOSE -Wno-import -g -O2 -fgnu-runtime -fconstant-string-class=NSConstantString -I. -I /usr/include/GNUstep -I/usr/include/GNUstep -o a.out source_file.m -lobjc -lgnustep-base"
}


class Rextester(commands.Cog):
    def __init__(self, client):
        self.client = client
        categories.addToCategory("misc", self)

    async def __fetch(self, session, data):
        async with session.get("https://rextester.com/rundotnet/api", data=data) as response:
            return await response.json()

    @commands.command(
        aliases=['rex'],
        description="Run code in multiple programming languages.",
        usage="k.rextester <language> <code>"
    )
    async def rextester(self, ctx, lang: str, *, code: str):
        code = code.replace("```", "")
        if lang.lower() not in languages:
            raise commands.UserInputError(f"Language {lang} is not recognized.")

        data = {
            "LanguageChoice": languages.get(lang.lower()),
            "Program": code,
            "Input": "",
            "CompilerArgs": compiler_args.get(lang.lower(), "")
        }

        async with aiohttp.ClientSession() as session:
            response = await self.__fetch(session, data)
            if response['Errors']:
                embed = easystyle.embed(title="Finished with errors.", description=response['Stats'],
                                        color=discord.Color.red())
                embed.add_field(name="Errors", value=f"```\n{response['Errors']}\n```", inline=False)
                if response['Warnings']:
                    embed.add_field(name="Warnings", value=f"```\n{response['Warnings']}\n```", inline=False)
                embed.add_field(name="Result", value=f"```\n{response['Result']}\n```", inline=False)
                return await ctx.send(ctx.author.mention, embed=embed)
            elif response['Warnings']:
                embed = easystyle.embed(title="Finished with warnings.", description=response['Stats'],
                                        color=discord.Color.gold())
                embed.add_field(name="Warnings", value=f"```\n{response['Warnings']}\n```", inline=False)
                embed.add_field(name="Result", value=f"```\n{response['Result']}\n```", inline=False)
                return await ctx.send(ctx.author.mention, embed=embed)
            else:
                embed = easystyle.embed(title="Finished.", description=response['Stats'], color=discord.Color.green())
                embed.add_field(name="Result", value=f"```\n{response['Result']}\n```", inline=False)
                return await ctx.send(ctx.author.mention, embed=embed)


def setup(client):
    client.add_cog(Rextester(client))
