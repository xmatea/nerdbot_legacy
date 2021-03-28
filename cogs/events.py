import discord
from discord.ext import commands
import datetime

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.hidden = True

def setup(bot):
    bot.add_cog(EventHandler(bot))
