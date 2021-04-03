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
DEV = os.getenv("DEV");
Config = process.readjson('config.json')
logging.basicConfig(level=logging.INFO)
prefix = Config.prefix

if DEV == 'True':
    prefix = os.getenv("PREFIX")

# define NerdBot class
class NerdBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=prefix)

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
    if DEV == "False":
        channel = bot.get_guild(Config.home_guild).get_channel(Config.log_channel)
        await channel.send(embed=discord.Embed(title="Nerdbot ready!", timestamp=datetime.now()))

bot.run(TOKEN)
