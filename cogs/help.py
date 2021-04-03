import discord
from discord.ext import commands
from process import readjson
from datetime import datetime

Config = readjson('config.json')
speech = readjson('speech.json')

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = True
        self.name = 'Help'

    @commands.command()
    async def help(self, ctx, *args):
        if not args:
            # List all commands in an embed
            embed = discord.Embed(title=":bar_chart: Help :bar_chart:", colour=int(speech.helpembed.embedcolour), timestamp=datetime.now())
            embed.description = f"{speech.helpembed.helptext}".format(Config.prefix)

            for c in self.bot.cogs:
                cog = self.bot.get_cog(c)
                if not cog.hidden:
                    text=""
                    for cmd in cog.get_commands():
                        if not cmd.hidden:
                            text += f"{Config.prefix}{cmd.name}\n"
                    embed.add_field(name=c, value=text)
            await ctx.send(content="", embed=embed)

        elif self.bot.get_cog(args[0].lower().capitalize()):
            cog = self.bot.get_cog(args[0].lower().capitalize())
            if not cog.hidden:
                text=""
                embed = discord.Embed(title=f"{cog.name} commands",colour=int(speech.helpembed.embedcolour))
                for cmd in cog.get_commands():
                    if not cmd.hidden:
                        text += f"{cmd.name} - {cmd.brief}\n"
                embed.add_field(name="List of commands", value=text)
                await ctx.send(content="", embed=embed)
                return

        elif self.bot.get_command(args[0].lower()):
            cmd = self.bot.get_command(args[0].lower())
            if not cmd.hidden:
                embed = discord.Embed(title=f"{cmd.name}",colour=int(speech.helpembed.embedcolour))
                text = f"{cmd.help}".format(Config.prefix)
                embed.add_field(name="Help and usage", value=text)
                await ctx.send(content="", embed=embed)
                return

        else:
            await ctx.send("I'm sorry, I can't find that command...")

def setup(bot):
    bot.add_cog(Help(bot))
