import discord
import os
from pymongo import MongoClient
import techpowerup as tpudb

## Initialising MongoDB connection, database, and collection.

print("Initialising MongoClient")
mongodb_connection_url = f"mongodb://root@${os.environ.get('MONGODB_PASSWORD')}mongo/techpowerup?authSource=admin"
mongo_client = MongoClient(mongodb_connection_url)
database = mongo_client.get_database()

# CPU Collection
cpu_collection = database["CPU"]

# GPU Collection
gpu_collection = database["GPU"]

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

## Thermal paste command
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

## /ping Command
@bot.command(description="Check if the bot is online or not.")
async def ping(ctx):
    await ctx.respond(f"pong! with a latency of {bot.latency * 1000}ms.")

## /benchmark
@bot.command(descrption="Provides with the list of benchmarks and stress tests for various PC components")
async def benchmark(ctx):
    await ctx.respond("https://discord.com/channels/1039926726320468151/1040148136695439451/1097182278137954414")

## /psutierlist
@bot.command(descrption="Provides with the Cultist PSU Tier list")
async def psutierlist(ctx):
    await ctx.respond("https://cultists.network/140/psu-tier-list/")

## /vendors
@bot.command(descrption="Provides with the list of Trusted Online Vendors")
async def vendors(ctx):
    await ctx.respond("https://discord.com/channels/1039926726320468151/1040148136695439451/1075327876125163560")


## UV/OC command group
uvoc = discord.SlashCommandGroup("uvoc", "Undervolt and Overclocking guides.")

# undervolt
@uvoc.command(descrption="Provides with the guide to Undervolt your GPU/CPU")
async def undervolt(ctx):
    await ctx.respond("https://discord.com/channels/1039926726320468151/1111113878722596905")

# overclock
@uvoc.command(descrption="Provides with the guide to Overclock your GPU/CPU/Memory")
async def overclock(ctx):
    await undervolt(ctx)

bot.add_application_command(uvoc)


## Techpowerup Database commands
techpowerup = discord.SlashCommandGroup("techpowerup", "Provides with CPU and GPU specs and detailed spec links from Techpower Up database")

# CPU DB [/techpowerup cpu]
@techpowerup.command(description="Provides with CPU Specs and Detailed specs link")
async def cpu(
     ctx,
     brand: discord.Option(discord.SlashCommandOptionType.string, choices=["AMD", "Intel", "VIA"]),
     name: discord.Option(discord.SlashCommandOptionType.string)
):
    search_result = tpudb.searchcpu({
        "Brand": brand,
        "query" : name
    })
    if not search_result:
        ctx.respond(f"No CPUs found with the name '{name}' under brand '{brand}'")
    if type(search_result) == tpudb.CPU:
        ctx.respond(f"We found the exact CPU! Embed is WIP.")
    if type(search_result) == list:
        ctx.respond(f"Multiple CPUs found. List selection is WIP.")

bot.add_application_command(techpowerup)


bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
