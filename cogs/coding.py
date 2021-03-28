import discord
from discord.ext import commands
from process import readjson, colour_convert
import random
from PIL import Image
import requests
from io import BytesIO
import numpy
import html_module


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
            #raise commands.MissingRequiredArgument
            await ctx.send("aaaa")
        url = ctx.message.attachments[0].url

        img = Image.open(requests.get(url, stream=True).raw)
        rgb_r = img.load()[1,1]
        hex_r = '%02x%02x%02x' % rgb_r
        embed = discord.Embed(title="colour", colour=colour_convert(hex_r))
        embed.description = f"{hex_r}"
        await ctx.send(content="", embed=embed)


    @commands.command()
    async def html_to_img(self, ctx, *, html):
        if len(html) == 0:
            rasie commands.MissingRequiredArgument
        else:
            img = await html_module.convert_to_img(html)
            img.seek(0)
            await ctx.send(file=discord.File(img, "image.png"))


def setup(bot):
    bot.add_cog(Coding(bot))
