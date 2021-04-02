import discord
from discord.ext import commands
import datetime
from process import readjson
from mongo import db as mongo
db = mongo.db

speech = readjson('speech.json')
config = readjson('config.json')

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.hidden = True
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        mongo.insert(guild, mongo.guildModel, db.guilds)
        channel = self.bot.get_guild(config.home_guild).get_channel(config.log_channel)
        await channel.send(embed=discord.Embed(title="Joined new server!", description=f"**Name:** {guild.name}\n**Size:** {guild.member_count} members\nCurrently in {len(self.bot.guilds)} servers!"))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        mongo.remove({"_id": guild.id}, db.guilds)
        channel = self.bot.get_guild(config.home_guild).get_channel(config.log_channel)
        await channel.send(embed=discord.Embed(title="Left a server!", description=f"**Name:** {guild.name}\n**Size:** {guild.member_count} members\nCurrently in {len(self.bot.guilds)} servers!"))


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(speech.err.noperm.format(error.missing_perms))

        if isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(speech.err.botnoperm.format(error.missing_perms))

        if isinstance(error, commands.UserInputError):
            helpstr = "Incorrect usage"
            try:
                helpstr = getattr(speech.help, ctx.command.name).format(config.prefix)
            except:
                print(f"warning: {ctx.command.name} has no usage description")

            embed = discord.Embed(title=f"Usage guide: {ctx.command.name}", description=helpstr)
            try:
                flagstr = ""
                flags = getattr(speech.flags, ctx.command.name)
                flags = flags._asdict()
                for flag in flags.keys():
                    flagstr +=f"\n`-{flag}`: {flags[flag]}"
                embed.add_field(name="Flags", value=flagstr)
            except:
                print(f"warning: {ctx.command.name} has no flag usage description")

            return await ctx.send(content="", embed=embed)

def setup(bot):
    bot.add_cog(EventHandler(bot))
