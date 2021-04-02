import discord
from discord.ext import commands
import process
import random
import graphing
import re
import flagparser
import mathparser as mp

config = process.readjson('config.json')

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Math'


    @commands.command(help=speech.help.calculate, brief=speech.brief.calculate, aliases=['calc','c', 'cal'])
    async def calculate(self, ctx, *, expr):
        res = mp.evaluate(expr)

        await ctx.send(content="", embed= discord.Embed(title=f"`{expr} = {res}`"))


    @commands.command(help=speech.help.plot, brief=speech.brief.plot)
    async def plot(self, ctx, expression: str, *, args):
        argument_flags = ('-range', '-rt')
        bool_flags = {'-rt': False, '-polar': False, '-surface': False, '-anim': False}

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

        elif bool_flags['-surface']:
            if bool_flags['-anim'] and bool_flags['-rt']:
                buf = graphing.animated_surface_rotate(expression, ranges['x'], ranges['y'], ranges['a'])
                buf.seek(0)

                await ctx.send(file=discord.File(buf, "anim.gif"))
            elif bool_flags['-anim']:
                buf = graphing.animated_surface(expression, ranges['x'], ranges['y'], ranges['a'])
                buf.seek(0)

                await ctx.send(file=discord.File(buf, "anim.gif"))
            elif bool_flags['-rt']:
                buf = graphing.static_surface_rotate(expression, ranges['x'], ranges['y'])
                buf.seek(0)

                await ctx.send(file=discord.File(buf, "anim.gif"))
            else:
                buf = graphing.static_surface(expression, ranges['x'], ranges['y'])
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
