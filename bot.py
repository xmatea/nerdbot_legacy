import discord
token = 'ODI1NDMwOTg4OTk3NTI1NTA0.YF90gw.K91ZIwxgCNhOecwq1XYzGQWx-Bg'

class Bot(discord.Client):
    async def on_message(self, msg):
        msg_arr = msg.content.split(" ")
        if not msg_arr[0] == "nerdbot":
            return

        cmd=msg_arr[1]
        args=msg_arr[2:]

        if cmd == 'nerdbot':
            await ctx.send('more')
  

nerdbot = Bot()
nerdbot.run(token)