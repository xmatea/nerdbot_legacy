import discord
from discord.ext import commands
import datetime
from process import readjson

speech = readjson('speech.json')

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.hidden = True

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(speech.err.noperm.format(error.missing_perms))

        if isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(speech.err.botnoperm.format(error.missing_perms))

        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("bad argument")



def setup(bot):
    bot.add_cog(EventHandler(bot))
