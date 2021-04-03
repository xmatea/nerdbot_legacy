import discord
from discord.ext import commands
from process import readjson, colour_convert
import random
from PIL import Image
import requests
from io import BytesIO
import numpy
import html_module
from image_processing import generate_palette
import random

Config = readjson('config.json')
speech = readjson('speech.json')

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Images'

    @commands.command(help=speech.help.palette, brief=speech.brief.palette)
    async def palette(self, ctx):
        url = ctx.message.attachments[0].url
        img = Image.open(requests.get(url, stream=True).raw).convert('RGB')

        palette = generate_palette(img)
        palette.seek(0)

        await ctx.send(file=discord.File(palette, "palette.png"))

    @commands.group(help=speech.help.colour_from_img, brief=speech.brief.colour_from_img, aliases=["color_from_img"])
    async def colour_from_img(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.UserInputError()

    @colour_from_img.command(aliases=["-m"])
    async def mean(self, ctx):
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


    @colour_from_img.command(aliases=["-r"])
    async def random(self, ctx):
        url = ctx.message.attachments[0].url
        img = Image.open(requests.get(url, stream=True).raw).convert('RGB')

        rgb = random.choice(list(zip(*(iter(numpy.array(img.convert('RGB')).flatten().tolist()),) * 3)))
        hx = '%02x%02x%02x' % rgb

        embed = discord.Embed(title="Random colour", colour=colour_convert(hx), description="Image mean colour value:")
        embed.add_field(name="HEX", value=hx)
        embed.add_field(name="RGB", value=f"({rgb[0]}, {rgb[1]}, {rgb[2]})")
        embed.add_field(name="Integer", value=colour_convert(hx))
        await ctx.send(content="", embed=embed)

def setup(bot):
    bot.add_cog(Images(bot))