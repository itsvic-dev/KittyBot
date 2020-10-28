import logging
import os

log = logging.getLogger(__name__)


def loadCogs(client):
    log.info("Loading cogs.")
    for cog in [file.split(".")[0] for file in os.listdir("cogs") if file.endswith(".py")]:
        try:
            client.load_extension(f"cogs.{cog}")
        except Exception as e:
            log.error(f"Failed loading cog {cog}: {type(e).__name__}: {str(e)}")
        else:
            log.info(f"Loaded cog {cog}.")
    log.info("Finished loading cogs.")
