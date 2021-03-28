import discord
from discord.ext import commands
import process
import random

config = process.readjson('config.json')

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.name = 'Math'

    @commands.command()
    async def plot(self, ctx, *args):
        await ctx.send("plotting, please wait...")

def setup(bot):
    bot.add_cog(Math(bot))