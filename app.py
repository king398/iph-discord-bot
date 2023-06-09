import discord
import os

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

# Thermal paste command
@bot.command(descrption="Provides with the list of reliable thermal pastes")
async def thermalpaste(ctx):
        await ctx.respond("""
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

@bot.command(description="Check if the bot is online or not.")
async def ping(ctx):
    await ctx.respond(f"pong! with a latency of {bot.latency * 1000}ms.")

@bot.command(descrption="Provides with the list of benchmarks and stress tests for various PC components")
async def benchmark(ctx):
    await ctx.respond("https://discord.com/channels/1039926726320468151/1040148136695439451/1097182278137954414")

@bot.command(descrption="Provides with the Cultist PSU Tier list")
async def psutierlist(ctx):
    await ctx.respond("https://cultists.network/140/psu-tier-list/")

@bot.command(descrption="Provides with the list of Trusted Online Vendors")
async def vendors(ctx):
    await ctx.respond("https://discord.com/channels/1039926726320468151/1040148136695439451/1075327876125163560")

uvoc = discord.SlashCommandGroup("uvoc", "Undervolt and Overclocking guides.")

@uvoc.command(descrption="Provides with the guide to Undervolt your GPU/CPU")
async def undervolt(ctx):
    await ctx.respond("https://discord.com/channels/1039926726320468151/1111113878722596905")

@uvoc.command(descrption="Provides with the guide to Overclock your GPU/CPU/Memory")
async def overclock(ctx):
    await undervolt(ctx)

bot.add_application_command(uvoc)



bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
