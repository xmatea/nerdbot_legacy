import discord
from discord.ext import commands
import process
import random
import graphing
import re
import flagparser
import mathparser as mp

config = process.readjson('config.json')
speech = process.readjson('speech.json')

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
    async def plot(self, ctx, *, args):
        if not args:
            raise commands.UserInputError()
        try:
            flags = ('-range', '-rt')
            bool_flags = {'-rt': False}
            default_ranges = {'x': (0,10), 'y': (0,10), 'theta': (0, mp.evaluate('2*pi')), 'a': (0,10)}
            ranges = {}
            animation = False
            surface = False
            polar = False

            args = flagparser.format(args, flags)
            expression = args['content']

            animation = len(re.compile(r'\b(a)\b').findall(expression)) > 0
            surface = len(re.compile(r'\b(y)\b').findall(expression)) > 0
            polar = len(re.compile(r'\b(theta)\b').findall(expression)) > 0

            for flag in bool_flags.keys():
                if flag in args:
                    bool_flags[flag] = True

            if '-range' in args.keys():
                matches = re.findall('([a-zA-Z]+)=\[([^,\[\]]*),([^,\[\]]*)\]', args['-range'])
                if not matches:
                    raise commands.UserInputError()

                for m in matches:
                    ranges.update({m[0]: (mp.evaluate(m[1]), mp.evaluate(m[2])) })
            else:
                if animation: ranges.update({'a': default_ranges['a']})
                if surface: ranges.update({'y': default_ranges['y']})

                if polar:
                    ranges.update({'theta': default_ranges['theta']})
                else:
                    ranges.update({'x': default_ranges['x']})

            wait_message = await ctx.send(embed=discord.Embed(title=f"`Plotting {expression}`", description="Generating. Please wait..."))

            # PLOT GRAPH
            if polar:
                if animation:
                    buf = graphing.animated_polar(expression, ranges['theta'], ranges['a'])
                    buf.seek(0)

                    await ctx.send(file=discord.File(buf, "anim.gif"))
                    await wait_message.delete()
                else:
                    buf = graphing.static_polar(expression, ranges['theta'])
                    buf.seek(0)

                    await ctx.send(file=discord.File(buf, "image.png"))
                    await wait_message.delete()

            elif surface:
                if animation and bool_flags['-rt']:
                    buf = graphing.animated_surface_rotate(expression, ranges['x'], ranges['y'], ranges['a'])
                    buf.seek(0)

                    await ctx.send(file=discord.File(buf, "anim.gif"))
                    await wait_message.delete()
                elif animation:
                    buf = graphing.animated_surface(expression, ranges['x'], ranges['y'], ranges['a'])
                    buf.seek(0)

                    await ctx.send(file=discord.File(buf, "anim.gif"))
                    await wait_message.delete()
                elif bool_flags['-rt']:
                    buf = graphing.static_surface_rotate(expression, ranges['x'], ranges['y'])
                    buf.seek(0)

                    await ctx.send(file=discord.File(buf, "anim.gif"))
                    await wait_message.delete()
                else:
                    buf = graphing.static_surface(expression, ranges['x'], ranges['y'])
                    buf.seek(0)

                    await ctx.send(file=discord.File(buf, "image.png"))
                    await wait_message.delete()

            else:
                if animation:
                    buf = graphing.animated_cartesian(expression, ranges['x'], ranges['a'])
                    buf.seek(0)

                    await ctx.send(file=discord.File(buf, "anim.gif"))
                    await wait_message.delete()
                else:
                    buf = graphing.static_cartesian(expression, ranges['x'])
                    buf.seek(0)

                    await ctx.send(file=discord.File(buf, "image.png"))
                    await wait_message.delete()
        except Exception as e:
            await ctx.send(f"An error occurred!\nError: {e}")
            await wait_message.delete()

            raise commands.UserInputError()

def setup(bot):
    bot.add_cog(Math(bot))
