import discord
from discord.ext import commands
from process import readjson, colour_convert
import random
from PIL import Image
import requests
from io import BytesIO
import numpy
import html_module
import bf
import colouring


config = readjson('config.json')
speech = readjson('speech.json')


class Coding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Coding'

    @commands.group(aliases=["img_to_color"])
    async def img_to_colour(self, ctx):
        if not ctx.message.attachments:
            raise commands.UserInputError()

        if ctx.invoked_subcommand is None:
            url = ctx.message.attachments[0].url
            img = Image.open(requests.get(url, stream=True).raw)
            na = numpy.array(img.convert('RGB'))

            rgb = tuple([int(i) for i in na.mean(axis=0).mean(axis=0)])
            hx = '%02x%02x%02x' % rgb

            embed = discord.Embed(title="Mean colour", colour=colour_convert(hx), description="Image mean colour value:")
            embed.add_field(name="HEX", value=hx)
            embed.add_field(name="RGB", value=f"({rgb[0]}, {rgb[1]}, {rgb[2]})")
            embed.add_field(name="Integer", value=colour_convert(hx))
            await ctx.send(content="", embed=embed)

    @img_to_colour.command(aliases=["-p"])
    async def palette(self, ctx):
        url = ctx.message.attachments[0].url
        img = Image.open(requests.get(url, stream=True).raw).convert('RGB')

        palette = colouring.generate_palette(img)
        palette.seek(0)

        await ctx.send(file=discord.File(palette, "palette.png"))


    @commands.command()
    async def html_to_img(self, ctx, *, html=None):
        if html is None:
            if not ctx.message.attachments:
                raise commands.BadArgument

            url = ctx.message.attachments[0].url
            html = requests.get(url).text

        img = await html_module.convert_to_img(html)
        img.seek(0)

        await ctx.send(file=discord.File(img, "image.png"))

    @commands.command()
    async def test(self):
        print("aa")


    @commands.command(aliases=["bf"]) #I'M' BROKEN, FIX MEEEEEEEEE
    async def brainfuck(self, ctx, *, code=None): # brainfuck minus input
        if code is None:
            if not ctx.message.attachments:
                raise commands.BadArgument

            url = ctx.message.attachments[0].url
            code = requests.get(url).text

        output = bf.run(code)

        await ctx.send(output)


def setup(bot):
    bot.add_cog(Coding(bot))
