import discord
from discord.ext import commands
import process
import random
from mongo import db as mongo
db = mongo.db

config = process.readjson('config.json')
speech = process.readjson('speech.json')

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = True
        self.name = 'Settings'

def setup(bot):
    bot.add_cog(Settings(bot))
