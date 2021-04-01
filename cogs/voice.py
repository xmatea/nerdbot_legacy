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
from types import SimpleNamespace

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
	def __init__(self, url, yt):
		self.duration = yt.length
		self.title = yt.title
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
		self.ctx = None
		self.is_paused = False

		self.current_song = SimpleNamespace(duration=0, title=None, url=None)
		self.current_song_started = datetime.now()
		self.song_time_left = lambda: timedelta(seconds=self.current_song.duration) - (datetime.now() - self.current_song_started)

		self.songs = lambda: [item.song for item in self._items]
		self.skip = lambda: self.play_next() if len(self._items) else self.ctx.voice_client.stop()


	def add(self, url, ctx):
		yt = YouTube(url)

		song = Song(url, yt)

		total_songs_duration = sum([s.duration for s in self.songs()])
		delay = self.song_time_left() + timedelta(seconds=total_songs_duration)
		delay = delay.total_seconds()
		timer = threading.Timer(delay, self.play_next)

		queue_item = QueueItem(song, ctx, timer)
		self._items.append(queue_item)

		timer.start()


	def play_next(self):
		self.current_song, self.ctx, timer = self._items.pop(0)

		if timer.is_alive():
			timer.cancel()

		self.current_song_started = datetime.now()

		buf = io.BytesIO()
		self.current_song.to_buffer(buf)
		buf.seek(0)

		audio_source = FFmpegPCMAudio(buf.read(), pipe=True)
		
		if self.ctx.voice_client.is_playing():
			self.ctx.voice_client.stop()
		
		self.ctx.voice_client.play(audio_source, after=None)
		self.is_paused = False


	def pause(self):
		if self.ctx is not None:
			self.ctx.voice_client.pause()
			self.is_paused = True

		else:
			print("Nothing to pause")


	def resume(self):
		if self.ctx is not None:
			self.ctx.voice_client.resume()
			self.is_paused = False

		else:
			print("Nothing to resume")


	def get_queue_songs(self):
		songs = self.songs()
		songs.insert(0, self.current_song)
		return songs



class Voice(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.hidden = False
		self.name = 'Voice'
		self.queue = Queue()


	@commands.command()
	async def join(self, ctx, *args):
		await ctx.author.voice.channel.connect()


	@commands.command()
	async def leave(self, ctx, *args):
		await ctx.voice_client.disconnect()


	@commands.command()
	async def skip(self, ctx):
		self.queue.skip()


	@commands.command()
	async def pause(self, ctx):
		self.queue.pause()


	@commands.command()
	async def resume(self, ctx):
		self.queue.resume()


	@commands.command()
	async def play(self, ctx, url=None):
		if not ctx.voice_client:
			await ctx.author.voice.channel.connect()

		if url is None:
			if self.queue.is_paused:
				self.queue.resume()
			else:
				raise commands.BadArgument
			
		self.queue.add(url, ctx)


	@commands.command()
	async def queue(self, ctx):
		queue_songs = self.queue.get_queue_songs()

		await ctx.send("\n".join([song.title for song in queue_songs]))


def setup(bot):
	bot.add_cog(Voice(bot))