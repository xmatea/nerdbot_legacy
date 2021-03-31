import discord
from discord.ext import commands
import process
from pytube import YouTube
import requests
import io

config = process.readjson('config.json')

# better FFmpegPCMAudio class; thanks https://github.com/Armster15 <3 =========================================
class FFmpegPCMAudio(discord.AudioSource):
	import subprocess
	import shlex
	from discord.opus import Encoder

	def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None):
		stdin = None if not pipe else source
		args = [executable]
		if isinstance(before_options, str):
			args.extend(shlex.split(before_options))
		args.append('-i')
		args.append('-' if pipe else source)
		args.extend(('-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'warning'))
		if isinstance(options, str):
			args.extend(shlex.split(options))
		args.append('pipe:1')
		self._process = None
		try:
			self._process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
			self._stdout = io.BytesIO(
				self._process.communicate(input=stdin)[0]
			)
		except FileNotFoundError:
			raise discord.ClientException(executable + ' was not found.') from None
		except subprocess.SubprocessError as exc:
			raise discord.ClientException('Popen failed: {0.__class__.__name__}: {0}'.format(exc)) from exc
	def read(self):
		ret = self._stdout.read(Encoder.FRAME_SIZE)
		if len(ret) != Encoder.FRAME_SIZE:
			return b''
		return ret
	def cleanup(self):
		proc = self._process
		if proc is None:
			return
		proc.kill()
		if proc.poll() is None:
			proc.communicate()

		self._process = None
# =============================================================================================================


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
		if not ctx.voice_client:
			self.join(ctx)
			
		buf = io.BytesIO()

		audio_stream = YouTube(url).streams.filter(only_audio=True).first()
		audio_stream.stream_to_buffer(buf)

		buf.seek(0)

		audio_source = FFmpegPCMAudio(buf.read(), pipe=True)

		if not ctx.voice_client.is_playing():
			ctx.voice_client.play(audio_source, after=None)


def setup(bot):
	bot.add_cog(Voice(bot))