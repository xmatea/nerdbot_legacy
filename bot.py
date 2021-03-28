# init
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from datetime import date, datetime
import process
import logging

# load and read configurations
load_dotenv()
TOKEN = os.getenv("TOKEN");
Config = process.readjson('config.json')
logging.basicConfig(level=logging.INFO)

# define NerdBot class
class NerdBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=Config.prefix)

# create bot instance
bot = NerdBot()

# read and load command groups
bot.remove_command('help')
bot.remove_cog('general')
for file in os.listdir("cogs"):
    if file.endswith('.py'):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("nerding"))
    print("Nerdbot started at {0}\nLoaded {1} cog(s) and commands: {2}".format(datetime.now().strftime("%H:%M:%S"), len(bot.cogs), bot.command_prefix))

bot.run(TOKEN)
