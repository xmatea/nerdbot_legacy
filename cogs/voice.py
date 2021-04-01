import discord
from discord.ext import commands
import process
from pytube import YouTube
import requests
import io
import subprocess
import shlex
from discord.opus import Encoder
import threading
from datetime import datetime, timedelta

config = process.readjson('config.json')

# better FFmpegPCMAudio class; thanks https://github.com/Armster15 <3 =========================================
class FFmpegPCMAudio(discord.AudioSource):
	
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

class Song:
	def __init__(self, url, duration):
		self.duration = duration
		self.url = url

	def to_buffer(self, buf):
		YouTube(self.url).streams.filter(only_audio=True).first().stream_to_buffer(buf)


class QueueItem:
	def __init__(self, song, ctx, timer):
		self.song = song
		self.ctx = ctx
		self.timer = timer


	def __iter__(self):
		return iter((self.song, self.ctx, self.timer))


class Queue: # make async
	def __init__(self):
		self._items = []
		self.songs = lambda: [item.song for item in self._items]
		self.current_song_started = datetime.now()
		self.playing_duration = 0


	def add(self, url, ctx):
		yt = YouTube(url)

		song = Song(url, yt.length)

		total_songs_duration = sum([s.duration for s in self.songs()])
		time_since_start = (datetime.now() - self.current_song_started).total_seconds()
		delay = timedelta(seconds=self.playing_duration) - timedelta(seconds=time_since_start)
		delay = delay + timedelta(seconds=total_songs_duration)
		delay = delay.total_seconds()
		timer = threading.Timer(delay, self.play_next)

		queue_item = QueueItem(song, ctx, timer)
		self._items.append(queue_item)

		timer.start()


	def skip(self):
		pass


	def play_next(self):
		song, ctx, _ = self._items.pop(0)
		self.current_song_started = datetime.now()
		self.playing_duration = song.duration

		buf = io.BytesIO()
		song.to_buffer(buf)
		buf.seek(0)

		audio_source = FFmpegPCMAudio(buf.read(), pipe=True)
		
		if not ctx.voice_client.is_playing():
			ctx.voice_client.play(audio_source, after=None)


class Voice(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.hidden = False
		self.name = 'Voice'
		self.queue = Queue()


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
			await ctx.author.voice.channel.connect()
			
		self.queue.add(url, ctx)


def setup(bot):
	bot.add_cog(Voice(bot))