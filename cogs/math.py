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
    async def plot(self, ctx, expression: str, *args):
        argument_flags = ('-range')
        bool_flags = {'-rt': False}

        for arg in args:
            if arg in bool_flags.keys():
                bool_flags[arg] = True

        args = [arg for arg in args if arg not in bool_flags]
        args = flagparser.format(args, argument_flags)
        args = {**args, **bool_flags}

        #print(args)
        ranges = []
        if '-range' in args:

            for rang in args:
                r = re.match('[a-zA-Z]=\[\d+\.?\d*,\d+\.?\d*]', rang)
                if r:
                    min, max = re.findall('\d+\.?\d*', rang)
                    ranges.append({rang[0]: (min, max)})

        #parse string to math expression
        """
        func = lambda x: x**2+y
        x_range = (x_min, x_max)
        buf = graphing.static_surface(func, x_range)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, "anim.gif"))
        """

    @commands.command()
    async def polar_(self, ctx, expression: str, x_min: int, x_max: int, y_min: int, y_max: int):
        await ctx.send("no")

def setup(bot):
    bot.add_cog(Math(bot))
