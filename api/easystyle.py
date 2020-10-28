import discord

from api import vars


def embed(**embedkwargs) -> discord.Embed:
    if "color" not in embedkwargs and "colour" not in embedkwargs:
        embedkwargs.update({"color": discord.Color.from_rgb(232, 123, 185)})
    ret = discord.Embed(**embedkwargs)
    ret.set_footer(text=f"{vars.botname} | v{vars.version}", icon_url=vars.avatar)
    return ret
