import discord
from discord.ext import commands
import process
import random

config = process.readjson('config.json')

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Voice'

    @commands.command()
    async def play(self, ctx, *args):
        await ctx.send("now playing: ")

def setup(bot):
    bot.add_cog(Voice(bot))
