import discord
from discord.ext import commands
from process import readjson, colour_convert
import random
from PIL import Image
import requests
from io import BytesIO
import numpy
import html_module
from types import SimpleNamespace


config = readjson('config.json')
speech = readjson('speech.json')


class Coding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Coding'

    @commands.command(alias="img_to_color")
    async def img_to_colour(self, ctx):
        if not ctx.message.attachments:
            raise commands.BadArgument()

        url = ctx.message.attachments[0].url
        img = Image.open(requests.get(url, stream=True).raw)
        na = numpy.array(img.convert('RGB'))

        rgb = [int(i) for i in na.mean(axis=0).mean(axis=0)]
        hex = '%02x%02x%02x' % tuple(rgb)

        embed = discord.Embed(title="Mean colour", colour=colour_convert(hex), description="Image mean colour value:")
        embed.add_field(name="HEX", value=hex)
        embed.add_field(name="RGB", value=f"({tuple(rgb)[0]}, {tuple(rgb)[1]}, {tuple(rgb)[2]})")
        embed.add_field(name="Integer", value=colour_convert(hex))
        await ctx.send(content="", embed=embed)


    @commands.command()
    async def html_to_img(self, ctx, *, html=None):
        if html is None:
            if not ctx.message.attachments:
                raise commands.MissingRequiredArgument(SimpleNamespace(name="html"))

            url = ctx.message.attachments[0].url
            html = requests.get(url).text

        img = await html_module.convert_to_img(html)

        img.seek(0)
        await ctx.send(file=discord.File(img, "image.png"))


def setup(bot):
    bot.add_cog(Coding(bot))
