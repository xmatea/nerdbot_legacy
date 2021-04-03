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

    @commands.command(help=speech.help.say, brief=speech.brief.say)
    async def say(self, ctx, *, args):
        if not args:
            raise UserInputError

        await ctx.send(args)
        await ctx.message.delete()

    @commands.command(help=speech.help.embed, brief=speech.brief.embed, aliases=['e'])
    async def embed(self, ctx, *, args):
        if not args:
            raise UserInputError

        flags = ('-t', '-c', '-a')
        args = flagparser.format(args, flags, False)
        title = ""
        colour = config.default_embed_colour
        if not 'content' in args.keys():
            raise UserInputError

        if '-c' in args.keys():
            colour = int(args['-c'])

        if '-t' in args.keys():
            title = args['-t']

        embed=discord.Embed(title=title, description=args['content'], colour=colour)

        if '-a' not in args.keys():
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Fun(bot))
