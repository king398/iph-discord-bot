import discord
import os

class IPHClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}")
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content == '?_ping':
            await message.channel.send('pong')
        if message.content == '?_thermalpaste':
            await self.thermalpaste(message)
        if message.content == '?_benchmark' or message.content == '?_benchmarks':
            await message.reply("https://discord.com/channels/1039926726320468151/1040148136695439451/1097182278137954414")
        if message.content == '?_psutierlist':
            await message.reply("https://cultists.network/140/psu-tier-list/")
        if message.content == '?_vendors':
            await message.reply("https://discord.com/channels/1039926726320468151/1040148136695439451/1075327876125163560")
        if message.content == '?_undervolt' or message.content == '?_overclock':
            await message.reply("https://discord.com/channels/1039926726320468151/1111113878722596905")
    async def thermalpaste(self, message):
        await message.reply("""
**__Reliable thermal pastes__**

_Legend_:
PCM := Phase change material

**_Value for money_**
Arctic MX4
Arctic MX6
Cooler Master Mastergel Regular
Cooler Master Mastergel Pro
Noctua NT-H1
Gelid GC Extreme

**_Mid range_**
Noctua NT-H2

**_High End_**
Honeywell PTM7950 (PCM)
Kryonaut Extreme
Cooler Master Mastergel Maker
Cooler Master Cryofuze
""")

intents = discord.Intents.default()
intents.message_content = True

client = IPHClient(intents=intents)
client.run(os.environ.get('DISCORD_BOT_TOKEN'))
