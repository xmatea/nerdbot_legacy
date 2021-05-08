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
            embed = discord.Embed(title=":bar_chart: Help :bar_chart:", colour=int(Config.default_embed_colour))
            embed.description = f"{speech.helpembed.helptext}".format(Config.prefix)

            for c in self.bot.cogs:
                cog = self.bot.get_cog(c)
                if not cog.hidden:
                    text=""
                    for cmd in cog.get_commands():
                        if not cmd.hidden:
                            text += f"{Config.prefix}{cmd.name}\n"
                    embed.add_field(name=c, value=text)

            embed.add_field(name="Links and support", value="If you like me, please consider voting for me [here](https://discordbotlist.com/bots/nerdbot)!\n[Github repository](https://github.com/xmatea/nerdbot)", inline=False)
            embed.set_footer(text="NerdBot by mogzhey#5070 and tea#4001")
            await ctx.send(content="", embed=embed)

        elif self.bot.get_cog(args[0].lower().capitalize()):
            cog = self.bot.get_cog(args[0].lower().capitalize())
            if not cog.hidden:
                text=""
                embed = discord.Embed(title=f"{cog.name} commands",colour=int(Config.default_embed_colour))
                for cmd in cog.get_commands():
                    text += f"`{cmd.name}` - {cmd.brief}\n"
                embed.add_field(name="Full list of commands", value=text)
                await ctx.send(content="", embed=embed)
                return

        elif self.bot.get_command(args[0].lower()):
            cmd = self.bot.get_command(args[0].lower())
            if not cmd.hidden:
                embed = discord.Embed(title=f"{cmd.name.capitalize()}",colour=int(Config.default_embed_colour))
                text = f"{cmd.help}".format(Config.prefix)
                embed.add_field(name="Help and usage", value=text)
                try:
                    flagstr = ""
                    flags = getattr(speech.flags, cmd.name)
                    flags = flags._asdict()
                    for flag in flags.keys():
                        flagstr +=f"\n`-{flag}`: {flags[flag]}"
                    embed.add_field(name="Flags", value=flagstr, inline=False)
                except:
                    print(f"warning: {cmd.name} has no flag usage description")
                await ctx.send(content="", embed=embed)
                return

        else:
            await ctx.send("I'm sorry, I can't find that command...")

def setup(bot):
    bot.add_cog(Help(bot))
