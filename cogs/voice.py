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
	async def join(self, ctx, *args):
		channel = ctx.author.voice.channel
		await channel.connect()


	@commands.command()
	async def leave(self, ctx, *args):
		await ctx.voice_client.disconnect()


	@commands.command()
	async def play(self, ctx, url):
		url = YouTube(url).streams.filter(only_audio=True)[0].url

		audio_source = discord.FFmpegPCMAudio(url)

		if not ctx.voice_client.is_playing():
			ctx.voice_client.play(audio_source, after=None)


def setup(bot):
	bot.add_cog(Voice(bot))