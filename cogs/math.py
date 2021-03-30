import discord
from discord.ext import commands
import process
import random
import graphing
import re
import flagparser
from mathparser import MathParser

config = process.readjson('config.json')

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Math'

    @commands.command()
    async def plot(self, ctx, expression: str, *, args):
        argument_flags = ('-range', '-rt')
        bool_flags = {'-rt': False, '-polar': False}

        for flag in bool_flags.keys():
            if flag in args:
                bool_flags[flag] = True
                args = args.replace(flag, "")

        args = flagparser.format(''.join(args), argument_flags, True)
        ranges = {}

        if '-range' in args.keys():
            matches = re.findall('([a-zA-Z]+)=\[([^,\[\]].*?),([^,\[\]].*?)\]', args['-range'])
            if not matches:
                raise commands.UserInputError()

            for m in matches:
                ranges.update({m[0]: (m[1], m[2]) })


        if bool_flags['-polar']:
            buf = graphing.static_polar(expression, ranges['theta'])
        else:
            buf = graphing.static_cartesian(expression, (0, 10))

        buf.seek(0)
        await ctx.send(file=discord.File(buf, "image.png"))


def setup(bot):
    bot.add_cog(Math(bot))
