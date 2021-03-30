import discord
from discord.ext import commands
import datetime
from process import readjson

speech = readjson('speech.json')
config = readjson('config.json')

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

        if isinstance(error, commands.UserInputError):
            usagestr = "Incorrect usage"
            try:
                usagestr = getattr(speech.usage, ctx.command.name).format(config.prefix)
            except:
                print(f"warning: {ctx.command.name} has no usage description")
            embed = discord.Embed(title=f"[{ctx.command.name}] Usage", description=usagestr)
            return await ctx.send(content="", embed=embed)

def setup(bot):
    bot.add_cog(EventHandler(bot))
