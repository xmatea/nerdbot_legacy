import discord
from discord.ext import commands
from process import readjson, colour_convert
import requests
import html_module


config = readjson('config.json')
speech = readjson('speech.json')


class Coding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Coding'

    @commands.command(help=speech.help.html_to_img, brief=speech.brief.html_to_img)
    async def html_to_img(self, ctx, *, html=None):
        if html is None:
            if not ctx.message.attachments:
                raise commands.BadArgument

            url = ctx.message.attachments[0].url
            html = requests.get(url).text

        img = await html_module.convert_to_img(html)
        img.seek(0)

        await ctx.send(file=discord.File(img, "image.png"))


def setup(bot):
    bot.add_cog(Coding(bot))
