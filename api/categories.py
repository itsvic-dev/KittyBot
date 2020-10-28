import logging

from discord.ext import commands

categories = {}
categoryDesc = {
    "general": "General commands",
    "info": "Informative commands",
    "misc": "Miscellaneous commands",
    "mod": "Moderator commands",
    "fun": "Fun commands",
    "music": "Music commands"
}

log = logging.getLogger(__name__)


def addToCategory(category: str, cog: commands.Cog):
    cogName = str(type(cog).__name__)
    if categories.get(category) is None:
        categories.update({category: {}})
    categories[category].update({cogName: cog})
    log.info(f"Added {cogName} to {category}.")


def getCategoryCogs(category: str) -> dict:
    return categories.copy().get(category)


def getCategories():
    return categories.copy()


def getCategoryDesc(category: str):
    return categoryDesc.get(category, 'None')
