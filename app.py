import discord
import os

class IPHClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}")
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content == 'ping':
            await message.channel.send('pong')

inetnts = discord.Intents.default()
intents.message_content = True

client = IPHClient(intents=inetnts)
client.run(os.environ.get['DISCORD_BOT_TOKEN'])
