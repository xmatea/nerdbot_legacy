import discord
from discord.ext import commands
import process
import random
import graphing
import re
import flagparser

config = process.readjson('config.json')

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Math'

    @commands.command()
    async def plot(self, ctx, expression: str, *, args):
        argument_flags = ('-range')
        bool_flags = {'-rt': False, '-polar': False}

        for flag in bool_flags.keys():
            if flag in args:
                bool_flags[flag] = True
                args = args.replace(flag, "")

        args = flagparser.format(args, argument_flags)
        args = {**args, **bool_flags}
        print(args)
        ranges = {}
        if '-range' in args.keys():
            for rang in args['-range']:
                r = re.match('[a-zA-Z]+=\[-?\d+\.?\d*,-?\d+\.?\d*\]', rang)
                if r:
                    rmin, rmax = map(float, re.findall('-?\d+\.?\d*', rang))
                    ranges.update({rang[:rang.index('=')]: (rmin, rmax)})

        print(ranges)
        if args['-polar']:
            buf = graphing.static_polar(expression, ranges['theta'])
        else:
            buf = graphing.static_cartesian(expression, ranges['x'])
        buf.seek(0)

        await ctx.send(file=discord.File(buf, "image.png"))

    @commands.command()
    async def polar_(self, ctx, expression: str, x_min: int, x_max: int, y_min: int, y_max: int):
        await ctx.send("no")

def setup(bot):
    bot.add_cog(Math(bot)) 
