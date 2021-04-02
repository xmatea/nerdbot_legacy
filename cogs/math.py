import discord
from discord.ext import commands
import process
import random
import graphing
import re
import flagparser
from mathparser import MathParser

config = process.readjson('config.json')
speech = process.readjson('speech.json')

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Math'

    @commands.command(help=speech.help.calculate, brief=speech.brief.calculate)
    async def calculate(self, ctx, *, expr):
        mp = MathParser()
        res = mp.evaluate(expr)

        await ctx.send(content="", embed= discord.Embed(title=f"`{expr} = {res}`"))

    @commands.command(help=speech.help.plot, brief=speech.brief.plot)
    async def plot(self, ctx, expression: str, *, args):
        argument_flags = ('-range', '-rt')
        bool_flags = {'-rt': False, '-polar': False, '-anim': False}

        mp = MathParser()

        for flag in bool_flags.keys():
            if flag in args:
                bool_flags[flag] = True
                args = args.replace(flag, "")

        args = flagparser.format(''.join(args), argument_flags, True)
        ranges = {}

        if '-range' in args.keys():
            matches = re.findall('([a-zA-Z]+)=\[([^,\[\]]*),([^,\[\]]*)\]', args['-range'])
            if not matches:
                raise commands.UserInputError()

            for m in matches:
                ranges.update({m[0]: (mp.evaluate(m[1]), mp.evaluate(m[2])) })

        if bool_flags['-polar']:
            if bool_flags['-anim']:
                buf = graphing.animated_polar(expression, ranges['theta'], ranges['a'])
                buf.seek(0)

                await ctx.send(file=discord.File(buf, "anim.gif"))
            else:
                buf = graphing.static_polar(expression, ranges['theta'])
                buf.seek(0)

                await ctx.send(file=discord.File(buf, "image.png"))
        else:
            if bool_flags['-anim']:
                buf = graphing.animated_cartesian(expression, ranges['x'], ranges['a'])
                buf.seek(0)

                await ctx.send(file=discord.File(buf, "anim.gif"))
            else:
                buf = graphing.static_cartesian(expression, ranges['x'])
                buf.seek(0)

                await ctx.send(file=discord.File(buf, "image.png"))




def setup(bot):
    bot.add_cog(Math(bot))
