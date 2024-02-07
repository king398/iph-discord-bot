import discord
import os
import techpowerup as tpudb
from utils import *
import logging
import random
from social_embeder import *
#DEBUG from dotenv import load_dotenv


logger=logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#DEBUG load_dotenv()

bot = discord.Bot(command_prefix='?_', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.event
async def on_message(message):
    social_media = check_social(message.content)
    if message.author == bot.user:
        return
    elif str(message.author.id) == '714745155835527198' and check_soy(message.content.lower()):
#        await message.reply("Cope, Mald, and Seethe Lodu")
        await message.delete()
    elif "4090" in message.content and "melt" in message.content:
        await message.reply("Another one! <:xddICANT:1047485587688525874>")
    elif bot.user in message.mentions:
        await message.reply(mentioned_me())
    elif '<@&1127987418197405807>' in message.content:
        await message.reply("Panch hazaar launde dikh jaane chahiye <:xdd666:1047058134486757417>")
    elif '<@&1158756290261160016>' in message.content:
        await message.reply("https://tenor.com/n1VZhJ8Bumt.gif")
    elif 'uwu' == message.content.lower():
        await message.reply("[UwU](https://files.mostwanted002.page/i_have_your_ip.mp4)")
    elif str(message.author.id) == '85614143951892480':
        await message.reply(["Chuppp bkl!! <:bahinchod:1076143675811319848>", "hhattt madarchod <:bahinchod:1076143675811319848>", "abeyy nikall lawde <:bahinchod:1076143675811319848>"][random.randint(0,2)])
    elif social_media[0]:
        new_message = ''
        if social_media[1] == "Twitter":
            new_message = embed_twitter(message=message.content)
        if social_media[1] == "Instagram":
            if "/reel/" in message.content:
                url = find_url(message.content)
                new_message = embed_reel(url[0])
            else:
                new_message = embed_instagram(message=message.content)
        if social_media[1] == "Reddit":
            new_message = embed_reddit(message=message.content)
        webhook = await message.channel.create_webhook(name=message.author.name)
        await webhook.send(str(new_message), username=message.author.name, avatar_url=message.author.display_avatar)
        await message.delete()
        webhooks = await message.channel.webhooks()
        for webhook in webhooks:
                await webhook.delete()



## Thermal paste command
# PROD Channel ID : 1040148136695439451
# PROD Message ID : 1108449206043164742
@bot.command(descrption="Provides with the list of reliable thermal pastes")
async def thermalpaste(ctx):
        channel = await ctx.guild.fetch_channel(1040148136695439451)
        message_content = await channel.fetch_message(1108449206043164742)
        await ctx.respond(message_content.content)

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

## /mouseguide
@bot.command(description="Guide to choose the perfect gaming mouse")
async def mouseguide(ctx):
    await ctx.respond("https://1-hp.org/blog/hpforgamers/how-to-choose-a-gaming-mouse-ergonomics-calculator/")


## /clearCMOS
@bot.command(description="Instructions to clear CMOS on modern motherboard")
async def clearcmos(ctx):
    message = """
If your motherboard has a Clear CMOS button on the motherboard I/O, use that as instructed in the motherboard manual, else locate CLEAR CMOS pins on your motherboard (refer your motherboard's manual for motherboard layout. They are usually named as CLR_CMOS, CLRCMOS1, CLRRTC, etc. depending on the motherboard vendor.) and follow the steps below.

1. Turn off your PC.
2. Disconnect your PC from AC Mains (Disconnect PSU from wall outlet).
3. Press and hold power button for 5-10 seconds to flush power from the system.
4. Take a screw driver and short the Clear CMOS pins for 2-3 seconds.
5. Connect your PSU back to wall outlet.
6. Turn on the PC. You should be greeted with BIOS screen requesting action for further setup.
"""
    await ctx.respond(message)


## /vendors
@bot.command(descrption="Provides with the list of Trusted Online Vendors")
async def vendors(ctx):
    await ctx.respond("https://discord.com/channels/1039926726320468151/1040148136695439451/1075327876125163560")

## /backupsolution
@bot.command(description="Provides with the link to UPS/Inverter Guide")
async def backupsolution(ctx):
    await ctx.respond("https://discord.com/channels/1039926726320468151/1123222529503416371")

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
     name: discord.Option(discord.SlashCommandOptionType.string, description="Exact or part of the SKU to look for."),
     igpu: discord.Option(discord.SlashCommandOptionType.string, choices=["Yes", "No"], required=False, description="Does it have an iGPU?", default=False),
     multiplier: discord.Option(discord.SlashCommandOptionType.string, choices=["Locked", "Unlocked"], required=False, description="Is the multiplier Locked or Unlocked?", default=False),
     class_of_cpu: discord.Option(discord.SlashCommandOptionType.string, required=False, choices=["Desktop", "Server", "Mobile", "Mobile Server"], description="Product Class of the CPU (Note: Only Intel has 'Mobile Server' class products.)", default=False)
):
    search_result = tpudb.searchcpu({
        "Brand": brand,
        "Name" : name,
        "iGPU" : igpu,
        "Product Class": class_of_cpu,
        "Multiplier": multiplier
    })
    if not search_result:
        await ctx.respond(f"No CPUs found with the name '{name}' under brand '{brand}' using your filters. Try again.")
    elif type(search_result) == tpudb.CPU:
        embedded_result = build_cpu_embed(search_result)
        await ctx.respond(f"We found the exact CPU!", embed=embedded_result)
    elif type(search_result) is list and len(search_result) < 25:
        await ctx.respond("Multiple CPUs found. Please pick one:", view=CPUSelectorView(cpu_list=cpu_list_builder(search_result)))
    elif len(search_result) > 25:
        await ctx.respond("Too many results. Please refine your search by choosing additional filter")
bot.add_application_command(techpowerup)



## /ryzenmobile
@bot.command(description="Naming scheme for Ryzen Mobile CPUs/APUs")
async def ryzenmobile(ctx):
    naming_scheme = """
## Ryzen Mobile CPU/APU Naming Guide



```
Ryzen 5 7640U -> Form Factor
        ||||---> Feature Isolation
        |||----> Architecture
        ||-----> Market Segment
        |------> Portfolio Model Year
```        
1. Form Factor:
 - **HX** -> **55W+** _(Max Performance)_
 - **HS** -> **~35W+** _(Thing Gaming/Creator)_
 - **U** -> **15-28W** _(Premium Ultrathin)_
 - **C** -> **15-28W** _(Chromebook)_
 - **e** -> **9W** _(Fanless variant of 'U')_

2. Feature Isolation:
 - **0** -> _Lower Model within segment_
 - **5** -> _Upper Model within segment_

3. Architecture:
 - **1** -> **Zen1** | **Zen+**
 - **2** -> **Zen2**
 - **3** -> **Zen3** | **Zen3+**
 - **4** -> **Zen4**
 - **5** -> **Zen5**
etc.

4. Market Segment:
 - **1** -> **Athlon Silver**
 - **2** -> **Athlon Gold**
 - **3** -> **Ryzen 3**
 - **4** -> **Ryzen 3**
 - **5** -> **Ryzen 5**
 - **6** -> **Ryzen 5**
 - **7** -> **Ryzen 7**
 - **8** -> **Ryzen 7/9**
 - **9** -> **Ryzen 9**

5. Portfolio Model Year:
 - **7** -> **2023**
 - **8** -> **2024**
 - **9** -> **2025**
"""
    await ctx.respond(naming_scheme + "\n" + "https://files.mostwanted002.page/ryzen_mobile.jpg")



bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
