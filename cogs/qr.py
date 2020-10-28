import os

import aiohttp
import cv2
import discord
import numpy as np
import qrcode
from discord.ext import commands

from api import categories, easystyle


class QR(commands.Cog):
    def __init__(self, client):
        self.client = client
        categories.addToCategory("misc", self)

    async def __fetch(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if not response.content_type.startswith("image"):
                    return None
                return await response.read()

    @commands.command(
        aliases=['qr', 'createQR'],
        description="Creates a QR code.",
        usage="k.makeQR <data>"
    )
    async def makeQR(self, ctx, *, data: str):
        img = qrcode.make(data)
        path = f"/tmp/kitty-qr{str(ctx.message.id)}"
        img.save(path, format="png")
        embed = easystyle.embed(title="Here is your QR code!", description=data)
        embed.set_image(url="attachment://qr.png")
        await ctx.send(ctx.author.mention, embed=embed, file=discord.File(path, filename="qr.png"))
        os.remove(path)

    @commands.command(
        description="Reads from a QR code.",
        usage="k.readQR <image URL or attachment>"
    )
    async def readQR(self, ctx, *, imageURL: str = None):
        if imageURL is None:
            if len(ctx.message.attachments) == 0:
                raise commands.UserInputError("You need to supply an image (either as URL or attachment).")
            else:
                imageURL = ctx.message.attachments[0].url
        imageData = await self.__fetch(imageURL)
        if imageData is None:
            raise commands.UserInputError("The URL/attachment sent is not an image.")
        npData = np.frombuffer(imageData, np.uint8)
        img = cv2.imdecode(npData, flags=1)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)
        embed = easystyle.embed(title="Here's the QR code's data!", description=data)
        await ctx.send(ctx.author.mention, embed=embed)


def setup(client):
    client.add_cog(QR(client))
