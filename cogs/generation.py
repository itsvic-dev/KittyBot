import discord
from discord.ext import commands
from api import easystyle, categories
import os
import aiohttp
#from gsbl.stick_bug import StickBug
from filetype import filetype
from wand.image import Image as WandImage
from PIL import Image as PILImage, ImageDraw as PILImageDraw, ImageFilter as PILImageFilter
import io
import subprocess


class Generation(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        categories.addToCategory("fun", self)

    async def generationCallback(self, ctx: commands.Context, func, *, filename: str = "image", fileext: str = "png", embedded: bool = True):
        async def internalCall():
            try:
                async with ctx.channel.typing():
                    await func()
            except Exception as e:
                await self.client.get_cog("CommandExceptionHandler").on_command_error(ctx, e)
            else:
                embed = easystyle.embed(
                    title=f"Your {filename} is ready!"
                )
                if embedded:
                    embed.set_image(url=f"attachment://{filename}.{fileext}")
                await ctx.send(
                    ctx.author.mention,
                    embed=embed,
                    file=discord.File(f"/tmp/{str(ctx.message.id)}", filename=f"{filename}.{fileext}")
                )
            os.remove(f"/tmp/{str(ctx.message.id)}")

        self.client.loop.create_task(internalCall())

    @staticmethod
    def getURL(ctx: commands.Context, url: str) -> str:
        if len(ctx.message.mentions) != 0:
            return str(ctx.message.mentions[0].avatar_url)
        elif url is None:
            if len(ctx.message.attachments) != 0:
                return ctx.message.attachments[0].url
            else:
                return str(ctx.author.avatar_url)
        else:
            return url

    async def getImageData(self, ctx: commands.Context, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as resp:
                if not resp.content_type.startswith("image"):
                    await self.client.get_cog("CommandExceptionHandler").on_command_error(ctx, commands.UserInputError(
                        "The URL isn't an image."))
                    return None
                if resp.status != 200:
                    await self.client.get_cog("CommandExceptionHandler").on_command_error(ctx, commands.UserInputError(
                        "The server didn't say the request is OK."))
                    return None
                if resp.content_length is None:
                    await self.client.get_cog("CommandExceptionHandler").on_command_error(ctx, commands.UserInputError(
                        "The image is bigger than 10 MB, sorry!"))
                    return None
                if resp.content_length > 10 * 1024 * 1024:
                    await self.client.get_cog("CommandExceptionHandler").on_command_error(ctx, commands.UserInputError(
                        "The image is bigger than 10 MB, sorry!"))
                    return None
            async with session.get(url) as resp:
                if resp.status != 200:
                    await self.client.get_cog("CommandExceptionHandler").on_command_error(ctx, commands.UserInputError(
                        "The server didn't say the request is OK."))
                    return None
                # data = await resp.content.read(8 * 1024 * 1024)
                # the above doesnt work :pensive:
                data = await resp.read()
                if not filetype.guess_mime(data).startswith("image"):
                    await self.client.get_cog("CommandExceptionHandler").on_command_error(ctx, commands.UserInputError(
                        "The URL isn't an image."))
                    return None
                return data

    @commands.command(
        description="wow, such magik!!111!!",
        usage="k.magik [mention, image or URL]"
    )
    async def magik(self, ctx: commands.Context, url: str = None):
        async def gen():
            data = await self.getImageData(ctx, self.getURL(ctx, url))
            if data is None:
                return
            with WandImage(blob=data) as img:
                size = (img.width, img.height)
                smallSize = (int(img.width / 2), int(img.height / 2))
                img.liquid_rescale(*smallSize)
                img.liquid_rescale(*size)
                img.save(filename=f"/tmp/{str(ctx.message.id)}")
        await self.generationCallback(ctx, gen)

    @commands.command(
        description="Puts an image into the Windows 10 wallpaper (your avatar by default).",
        usage="k.windows [mention, image or URL]"
    )
    async def windows(self, ctx: commands.Context, url: str = None):
        async def gen():
            pos = (843, 217)
            size = (294, 294)
            data = await self.getImageData(ctx, self.getURL(ctx, url))
            if data is None:
                return
            layer1data = io.BytesIO(data)
            layer2bg = PILImage.open("./res/windows-bg.png")
            layer1 = PILImage.open(layer1data).convert("RGBA").resize(size, resample=PILImage.NEAREST)
            layer2 = PILImage.open("./res/windows.png")
            combined = PILImage.new('RGBA', layer2.size)
            combined.paste(layer2bg)
            combined.paste(layer1, box=pos, mask=layer1.getchannel('A'))
            combined.paste(layer2, mask=layer2.getchannel('A'))
            combined.save(f"/tmp/{str(ctx.message.id)}", format="png")
        await self.generationCallback(ctx, gen)

    @commands.command(
        description="WHAT? HOW",
        usage="k.how [mention, image or URL]"
    )
    async def how(self, ctx: commands.Context, url: str = None):
        async def gen():
            data = await self.getImageData(ctx, self.getURL(ctx, url))
            if data is None:
                return
            sourcedata = io.BytesIO(data)
            source = PILImage.open(sourcedata)
            if source.size[0] < 400 or source.size[1] < 400:
                source = source.resize((source.size[0] * 5, source.size[1] * 5), resample=PILImage.NEAREST)
            source.thumbnail((1024, 1024))
            how = PILImage.open("./res/how.png")
            paddedSize = (source.size[0] + 60, source.size[1] + 100 + how.size[1])
            howPosition = (
                int((paddedSize[0] / 2) - (how.size[0] / 2)),
                int(paddedSize[1] - 20 - how.size[1])
            )
            combined = PILImage.new('RGB', paddedSize)
            combinedDraw = PILImageDraw.Draw(combined)
            combinedDraw.rectangle([10, 10, source.size[0] + 50, source.size[1] + 50], outline=0xffffff, width=10)
            combined.paste(source, (30, 30))
            combined.paste(how, howPosition)
            combined = combined.filter(PILImageFilter.GaussianBlur(2))
            combined.save(f"/tmp/{str(ctx.message.id)}", format="JPEG", quality=5)
        await self.generationCallback(ctx, gen, fileext="jpg")

    @commands.command(
        description="What if you wanted to go to heaven, but God said...",
        usage="k.godsaid [mention, image or URL]"
    )
    async def godsaid(self, ctx, url: str = None):
        async def gen():
            data = await self.getImageData(ctx, self.getURL(ctx, url))
            if data is None:
                return
            pos = (383, 365)
            size = (367, 372)
            sourcedata = io.BytesIO(data)
            source = PILImage.open(sourcedata).resize(size, resample=PILImage.NEAREST)
            template = PILImage.open("./res/godsaid.png")
            template.paste(source, box=pos)
            template.save(f"/tmp/{str(ctx.message.id)}", format="png")
        await self.generationCallback(ctx, gen)

    @commands.command(
        description="we're putting you into a box and shipping it to brazil",
        usage="k.brazil [mention, image or URL]"
    )
    async def brazil(self, ctx: commands.Context, url: str = None):
        async def gen():
            data = await self.getImageData(ctx, self.getURL(ctx, url))
            if data is None:
                return
            avatarData = io.BytesIO(data)
            avatar = PILImage.open(avatarData).resize((435, 435))
            bg = PILImage.open("./res/brazil-bg.png")
            top = PILImage.open("./res/brazil-front.png")
            bg.paste(avatar, box=(295, 148))
            bg.paste(top, mask=top.getchannel('A'))
            bg = bg.filter(PILImageFilter.GaussianBlur(2))
            bg.convert("RGB").save(f"/tmp/{str(ctx.message.id)}", format="JPEG", quality=10)
        await self.generationCallback(ctx, gen, fileext="jpg")

    @commands.command(
        description="Mutahar laughs at your pic",
        usage="k.mutalaugh [mention, image or URL]"
    )
    async def mutalaugh(self, ctx: commands.Context, url: str = None):
        async def gen():
            data = await self.getImageData(ctx, self.getURL(ctx, url))
            if data is None:
                return
            with open(f"/tmp/{str(ctx.message.id)}-temp", 'wb') as file:
                file.write(data)
            # filter made by dengr :seemsBlob:
            subprocess.Popen([
                "/usr/bin/env", "ffmpeg",
                "-i", "./res/mutalaugh.mp4",
                "-loop", "1",
                "-i", f"/tmp/{str(ctx.message.id)}-temp",
                "-t", "5",
                "-filter_complex", "[0:v]pad=iw*2:ih:iw:0[src];[1:v]scale=460:448[layer2];[src][layer2] overlay=0:0",
                "-f", "mp4",
                f"/tmp/{str(ctx.message.id)}"
            ]).wait()
            os.remove(f"/tmp/{str(ctx.message.id)}-temp")
        await self.generationCallback(ctx, gen, fileext="mp4", filename="video", embedded=False)

"""
    @commands.command(
        description="GET STICK BUGGED LOL",
        usage="k.gsb [mention, image or URL]"
    )
    async def gsb(self, ctx, url: str = None):
        async def gen():
            data = await self.getImageData(ctx, self.getURL(ctx, url))
            if data is None:
                return
            with open(f"/tmp/{str(ctx.message.id)}-temp", 'wb') as file:
                file.write(data)
            sb = StickBug(f"/tmp/{str(ctx.message.id)}-temp")
            sb.save_video(f"/tmp/{str(ctx.message.id)}.mp4")
            os.rename(f"/tmp/{str(ctx.message.id)}.mp4", f"/tmp/{str(ctx.message.id)}")
        await self.generationCallback(ctx, gen, fileext="mp4", filename="video", embedded=False)
"""

def setup(client):
    client.add_cog(Generation(client))
