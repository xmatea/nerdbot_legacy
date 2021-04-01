import discord
from discord.ext import commands
import process
import random
import flagparser


config = process.readjson('config.json')
speech = process.readjson('speech.json')


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Fun'

    @commands.command()
    async def say(self, ctx, *, args):
        if not args:
            raise UserInputError

        await ctx.send(args)
        await ctx.message.delete()

    @commands.command()
    async def embed(self, ctx, *, args):
        if not args:
            raise UserInputError

        flags = ('-t', '-c')
        args = flagparser.format(args, flags, False)
        title = ""
        colour = 00000000
        print(args)
        if not 'content' in args.keys():
            raise UserInputError

        if '-c' in args.keys():
            colour = int(args['-c'])

        if '-t' in args.keys():
            title = args['-t']

        await ctx.send(embed=discord.Embed(title=title, description=args['content'], colour=colour))
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Fun(bot))
