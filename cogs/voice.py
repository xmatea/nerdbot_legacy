import discord
from discord.ext import commands
import process
from pytube import YouTube
import requests
import io

config = process.readjson('config.json')

class Voice(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.hidden = False
		self.name = 'Voice'


	@commands.command()
	async def play(self, ctx, url):
		url = YouTube(url).streams[0].url
		video = io.BytesIO(requests.get(url, stream=True).content)
		video.seek(0)

		await ctx.send("Matea is SUPER hot 😍🥵")


def setup(bot):
	bot.add_cog(Voice(bot))
