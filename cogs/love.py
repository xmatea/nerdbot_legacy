import discord
from discord.ext import commands
import process
import random


config = process.readjson('config.json')
speech = process.readjson('speech.json')


class Love(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Love'

    @commands.command(help=speech.help.fact, brief=speech.brief.fact)
    async def fact(self, ctx, *args):
        ix = round(random.random() * (len(speech.facts)-1))
        await ctx(ix)
        fact = speech.facts[ix]
        await ctx.send(fact)

    @commands.command(help=speech.help.bestperson, brief=speech.brief.bestperson)
    async def bestperson(self, ctx, *args):
        await ctx.send("morgan")

def setup(bot):
    bot.add_cog(Love(bot))
