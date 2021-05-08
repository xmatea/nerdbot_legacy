import discord
from discord.ext import commands
import process
from pytube import YouTube, Playlist
import io
import asyncio
import subprocess
import shlex
from discord.opus import Encoder
import threading
from datetime import datetime, timedelta
from types import SimpleNamespace
import re
from youtubesearchpython import VideosSearch
import numpy as np


config = process.readjson('config.json')
speech = process.readjson('speech.json')

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
		self.image_url = yt.thumbnail_url
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

def fetch_youtube(url):
	songs=[]
	for u in url:
		try:
			yt = YouTube(u)
			songs.append(Song(u, yt))
			print(Song(u, yt).title)
		except:
			pass
	return songs

class Queue: # make async
	def __init__(self):
		self._items = []
		self.ctx = None
		self.is_paused = False
		self.current_song = SimpleNamespace(duration=0, title=None, url=None)
		self.current_song_started = datetime.now()
		self.song_time_left = lambda: timedelta(seconds=self.current_song.duration) - (datetime.now() - self.current_song_started)
		self.songs = lambda: [item.song for item in self._items]
		self.leave_timer = None


	async def add_many(self, url, ctx):
		loop = asyncio.get_running_loop()

		songs = await loop.run_in_executor(None, fetch_youtube, url)
		for song in songs:
			total_songs_duration = sum([s.duration for s in self.songs()])
			delay = self.song_time_left() + timedelta(seconds=total_songs_duration)
			delay = delay.total_seconds()
			timer = threading.Timer(delay, self.play_next)

			queue_item = QueueItem(song, ctx, timer)
			self._items.append(queue_item)
			timer.start()

			await self.reset_leave_timeout(ctx)

	async def add(self, url, ctx):
		yt = ""
		try:
			yt = YouTube(url)
		except Exception as e:
			await ctx.send("error")

		song = Song(url, yt)
		total_songs_duration = sum([s.duration for s in self.songs()])
		delay = self.song_time_left() + timedelta(seconds=total_songs_duration)
		delay = delay.total_seconds()
		timer = threading.Timer(delay, self.play_next)

		queue_item = QueueItem(song, ctx, timer)
		self._items.append(queue_item)
		timer.start()

		await self.reset_leave_timeout(ctx)


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


	def skip(self, index):
		if not index:
			if len(self._items):
				self.play_next()
			else:
				self.current_song = SimpleNamespace(duration=0, title=None, url=None)
				self.ctx.voice_client.stop()
		else:
			self._items.pop(index-1)


	async def reset_leave_timeout(self, ctx):
		if self.leave_timer and self.leave_timer.is_alive():
			self.leave_timer.cancel()

		if len(self._items) == 0 and self.current_song.duration == 0:
			delay = 120

		else:
			delay = sum([song.duration for song in self.songs()]) + self.song_time_left().total_seconds() + 120

		try:
			def leave_channel(ctx, loop):
				asyncio.ensure_future(ctx.voice_client.disconnect(), loop=loop)

			loop = asyncio.get_running_loop()
			self.leave_timer = threading.Timer(delay, leave_channel, [ctx, loop])
			print(delay)
			self.leave_timer.start()

		except Exception as e:
			print(e)


class Voice(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.hidden = False
		self.name = 'Voice'
		self.queues = {}
		self.formatted_time = lambda s: "%d:%02d:%02d" % (s / 3600, (s % 3600) / 60, s % 60) if s > 3600 else "%d:%02d" % (s / 60, s % 60)
		self.formatted_search = lambda res: "```" + "\n".join([f"{ix+1}: {r['title']}" for ix, r in enumerate(res)]) + "```"

	def get_queue(self, id):
		if not id in self.queues.keys():
			self.queues.update({id: Queue()})
		return self.queues[id]


	@commands.command(help=speech.help.play, brief=speech.brief.play)
	async def play(self, ctx, *, url=None):
		queue = self.get_queue(ctx.guild.id)

		if not ctx.voice_client:
			await ctx.invoke(self.bot.get_command("join"))

		if url is None:
			if queue.is_paused:
				queue.resume()
			else:
				raise commands.BadArgument()


		if not ("http://" in url or "https://" in url):
			search_term = url

			if "-list" in search_term:
				search_term = search_term.replace("-list", "")
				await ctx.invoke(self.bot.get_command("search"), search_term=search_term)

				return
			else:
				search = VideosSearch(search_term, limit=1)
				watch_id = search.result()["result"][0]["id"]

				url = f"https://www.youtube.com/watch?v={watch_id}"

		if "list" in url:
			try:
				await ctx.send("Adding songs, please wait...")
				playlist = Playlist(url)
				# may take time
				await queue.add_many(playlist.video_urls, ctx)

				songs = queue.get_queue_songs()

				await ctx.send(f"Added {len(songs)} songs from {playlist.title}")
				await ctx.send(embed=discord.Embed(title="Playing now! :musical_note:", description=f"**{songs[0].title}**\nDuration: {self.formatted_time(songs[0].duration)}"))

			except Exception as e:
				await ctx.send("An error occurred!")
				print(e)

		else:
			# may take time
			await queue.add(url, ctx)
			songs = queue.get_queue_songs()

			if len(songs) == 1:
				await ctx.send(embed=discord.Embed(title="Playing now! :musical_note:", description=f"**{songs[0].title}**\nDuration: {self.formatted_time(songs[0].duration)}"))
			else:
				playtime = sum(song.duration for song in songs[1:-1]) + queue.song_time_left().total_seconds()
				await ctx.send(embed=discord.Embed(title="Added to queue! :musical_note:", description=f"**{songs[-1].title}**\n Time until playing: {self.formatted_time(playtime)}"))


	@commands.command(help=speech.help.join, brief=speech.brief.join)
	async def join(self, ctx, *args):
		channel = ctx.author.voice

		if not channel:
			await ctx.send("You need to be in a voice channel to use this command.")
		await channel.channel.connect()
		await ctx.send(embed=discord.Embed(description=f":musical_note: Joined **{channel.channel.name}** :musical_note:"))

		queue = self.get_queue(ctx.guild.id)
		await queue.reset_leave_timeout(ctx)


	@commands.command(help=speech.help.leave, brief=speech.brief.leave)
	async def leave(self, ctx, *args):
		self.queue = Queue(ctx)
		await ctx.voice_client.disconnect()


	@commands.command(help=speech.help.skip, brief=speech.brief.skip)
	async def skip(self, ctx, index=0):
		queue = self.get_queue(ctx.guild.id)
		queue.skip(index)
		await ctx.send("Skipped song!")



	@commands.command(help=speech.help.pause, brief=speech.brief.pause)
	async def pause(self, ctx):
		queue = self.get_queue(ctx.guild.id)
		queue.pause()
		await ctx.send("Paused queue!")


	@commands.command(help=speech.help.resume, brief=speech.brief.resume)
	async def resume(self, ctx):
		queue = self.get_queue(ctx.guild.id)
		queue.resume()
		await ctx.send("Resumed queue!")


	@commands.command()
	async def search(self, ctx, *, search_term):
		if not search_term:
			raise commands.UserInputError()

		search = VideosSearch(search_term, limit=10)
		res = search.result()["result"]
		queue = self.get_queue(ctx.guild.id)

		# display search message
		send = self.formatted_search(res) + "\n Please wait until bot has finished reacting."
		msg = await ctx.send(embed=discord.Embed(title=f"Search results: {search_term}", description=send))


		#react to messages
		emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
		for emoji in emoji_list:
			await msg.add_reaction(emoji)

		def check(reaction, user):
			return user == ctx.message.author and reaction.emoji in emoji_list and reaction.message == msg

		react = None;
		try:
			reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
			react = reaction.emoji

		except asyncio.TimeoutError:
			await ctx.channel.send(embed=discord.Embed(description="**Search timed out.**"))
			await msg.clear_reactions()
		
		else:
			if not ctx.voice_client:
				channel = ctx.author.voices
				if not channel:
					await ctx.send("You need to be in a voice channel to use this command.")
				await channel.channel.connect()

			url = res[emoji_list.index(react)]['link']
			await ctx.invoke(self.bot.get_command("play"), url=url)
			await msg.clear_reactions()

	@commands.command()
	async def queue(self, ctx):
		queue = self.get_queue(ctx.guild.id)
		songs = queue.get_queue_songs()

		#if songs[0].title is None:
			#return await ctx.send(f"Queue is empty! Enter a voice channel and add song with `{config.prefix}play [youtube url]`")

		playlist = "Up next:\n"
		playtime = queue.song_time_left().total_seconds()
		total_playtime = playtime

		display_items = [f"**{ix+1}: [{self.formatted_time(sum([song.duration for song in songs[:ix]])+playtime)}]** {song.title}!\n" for ix, song in enumerate(songs[1:])]
		pages = [display_items[i:i + 20] for i in range(0, len(display_items), 20)]

		index = 0
		page_display = await ctx.send(embed=discord.Embed(title=f"Currently playing: {songs[0].duration} :musical_note:\nTime remaining: {self.formatted_time(playtime)}", description="".join(pages[0])).set_footer(text=f"Page {index+1} / {len(pages)}"))
		
		emoji_list = ["⬅", "➡"]
		for emoji in emoji_list:
			await page_display.add_reaction(emoji)

		def check(reaction, user):
			return reaction.emoji in emoji_list and reaction.message == page_display and user != self.bot.user

		looping = True
		while looping:
			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
				react = reaction.emoji

				if react == emoji_list[1]:
					index += 1
					try:
						await page_display.edit(embed=discord.Embed(title=f"Currently playing: {songs[0].title} :musical_note:\nTime remaining: {self.formatted_time(playtime)}", description="".join(pages[index])).set_footer(text=f"Page {index+1} / {len(pages)}"))
					except IndexError:
						pass
					await reaction.remove(user)

				elif react == emoji_list[0]:
					index -= 1
					try:
						await page_display.edit(embed=discord.Embed(title=f"Currently playing: {songs[0].title} :musical_note:\nTime remaining: {self.formatted_time(playtime)}", description="".join(pages[index])).set_footer(text=f"Page {index+1} / {len(pages)}"))
					except IndexError:
						pass
					await reaction.remove(user)


			except asyncio.TimeoutError:
				looping = False
				await page_display.clear_reactions()

def setup(bot):
	bot.add_cog(Voice(bot))