import discord
from discord.ext import commands
from process import readjson

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
            embed = discord.Embed(title="",colour=00000000)
            embed.description = f"Hello, my prefix is `{Config.prefix}`. Below is a list of my commands.\nFor more info on a category, type `help (category)`\n"
            for c in self.bot.cogs:
                cog = self.bot.get_cog(c)
                if not cog.hidden:
                    text=""
                    for cmd in cog.get_commands():
                        if not cmd.hidden:
                            text += f"{cmd.name}\n"
                    embed.add_field(name=c, value=text)
            await ctx.send(content="", embed=embed)

        elif len(args) > 1:
            await ctx.send("Please specify only one command or category.")


        elif self.bot.get_cog(args[0].lower().capitalize()):
            cog = self.bot.get_cog(args[0].lower().capitalize())
            if not cog.hidden:
                text=""
                embed = discord.Embed(title=f"{cog.name} commands",colour=00000000)
                for cmd in cog.get_commands():
                    if not cmd.hidden:
                        text += f"{cmd.name} - {cmd.brief}\n"
                embed.add_field(name="List of commands", value=text)
                await ctx.send(content="", embed=embed)
                return

        elif self.bot.get_command(args[0].lower()):
            cmd = self.bot.get_command(args[0].lower())
            if not cmd.hidden:
                embed = discord.Embed(title=f"{cmd.name}:",colour=00000000)
                text = f"{cmd.help}".format(Config.prefix)
                embed.add_field(name="Help and usage", value=text)
                await ctx.send(content="", embed=embed)
                return

        else:
            await ctx.send("I'm sorry, I can't find that command.")

def setup(bot):
    bot.add_cog(Help(bot))
