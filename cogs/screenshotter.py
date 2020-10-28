import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
import os
from api import easystyle, categories


class Screenshot(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client
        self.options = Options()
        self.options.headless = True
        self.options.add_argument("--proxy-server=socks5://127.0.0.1:9050")
        prefs = {"safebrowsing.enabled": True}
        self.options.add_experimental_option("prefs", prefs)
        categories.addToCategory("fun", self)

    """
    @commands.is_owner()
    @commands.command()
    async def _setSSProxy(self, ctx, proxy: str):  # we don't need this command anymore
        self.options = Options()
        self.options.headless = True
        self.options.add_argument("--proxy-server=" + proxy)
        config.set("proxy", "screenshot", proxy)
    """

    @commands.is_nsfw()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(
        aliases=["ss"],
        description="Screenshots a web page, then sends you the result.",
        usage="k.screenshot <URL>"
    )
    async def screenshot(self, ctx: commands.Context, *, url: str):
        if not url.startswith("https://"):
            raise commands.UserInputError("The URL must be HTTPS. Check if you have typed the URL correctly.")
        message = await ctx.send(embed=easystyle.embed(
            title="Give us a while, please!",
            description="Give us up to 30 seconds to properly load and screenshot the site, please!"
        ))
        quitFlag = False
        driver = webdriver.Chrome(options=self.options)
        try:
            driver.set_page_load_timeout(30)
            driver.set_window_size(1280, 720)
            driver.get(url)
            S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
            if S('Height') > 720 or S('Width') > 1280:
                driver.set_window_size(S('Width'), S('Height'))
            driver.save_screenshot(f"/tmp/{ctx.message.id}")

        except TimeoutException:
            await ctx.send(ctx.author.mention,
                           embed=easystyle.embed(title="Oops!",
                                                 description="Sorry, but the page took too long to load. Are "
                                                             "you sure the site isn't malicious?",
                                                 color=discord.Color.red()))
            quitFlag = True
        except WebDriverException:
            await ctx.send(ctx.author.mention,
                           embed=easystyle.embed(title="Oops!",
                                                 description="Sorry, but it seems like the page has crashed. "
                                                             "Check if you have typed the URL correctly.",
                                                 color=discord.Color.red()))
            quitFlag = True
        finally:
            await message.delete()
            # https://cdn.discordapp.com/attachments/724368480685523038/742284917089763368/unknown.png
            driver.quit()
            if quitFlag:
                return
        file = discord.File(f"/tmp/{ctx.message.id}", filename="ss.png")
        embed = easystyle.embed(
            title="Here is your screenshot!",
            description=f"The page you screenshotted is: {url}"
        )
        embed.set_image(url="attachment://ss.png")
        await ctx.send(
            file=file,
            embed=embed
        )
        os.remove(f"/tmp/{ctx.message.id}")


def setup(client):
    client.add_cog(Screenshot(client))
