import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, BotMissingPermissions

from mongo import db as mongo
from process import readjson
import time

Config = readjson('config.json')
speech = readjson('speech.json')

class Moderation(commands.Cog):  
	def __init__(self, bot): 
		self.bot = bot
		self.hidden = False
		self.name = 'Moderation'

	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.command(help=speech.help.clear, brief=speech.brief.clear)
	async def clear(self, ctx, args: int):
		a = args+1
		if a>=1000:
			return await ctx.send("That's a lot of messages haha, max bulk delete is 1000.")

		d = await ctx.channel.purge(limit=a)
		await ctx.send(f"Deleted {len(d)-1} messages!")

def setup(bot):
	bot.add_cog(Moderation(bot))