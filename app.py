import discord
import os
import techpowerup as tpudb
from utils import *
from datetime import timedelta
import logging
import random
import sys
from social_embeder import *
# DEBUG from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import upload_file
import json
import glob
import shutil
from tqdm import tqdm
import uuid
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image, ImageDraw, ImageFont
import time
from joblib import Parallel, delayed
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
count = 0
last_author = ''
# DEBUG load_dotenv()

bot = discord.Bot(command_prefix='?_', intents=discord.Intents.all())

allowed_image_types = ['png', 'jpg', 'jpeg', 'webp', ]
allowed_video_types = ['.mp4', '.mpeg', '.mov', '.avi', '.flv', '.mpg', '.webm', '.wmv', '.3gp']
allowed_media_types = allowed_image_types + allowed_video_types


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.event
async def on_message(message):
    global count
    global last_author
    social_media = check_social(message.content)
    if message.author == bot.user:
        return
    elif "4090" in message.content and "melt" in message.content:
        await message.reply("Another one! <:xddICANT:1047485587688525874>")
    elif bot.user in message.mentions:
        if count >= 0 and count <= 4:
            await message.reply(mentioned_me())
            count += 1
        if count >= 5:
            await message.reply("Ffs stop spamming mentions! <:Madge:1047485310369542225> or you'll be timed out")
            last_author = message.author
            count = -1
        if count == -1 and message.author == last_author:
            await message.author.timeout_for(timedelta(seconds=60), reason="Spamming bot mentions")
            count += 1
    elif '<@&1127987418197405807>' in message.content:
        await message.reply("Panch hazaar launde dikh jaane chahiye <:xdd666:1047058134486757417>")
    elif '<@&1158756290261160016>' in message.content:
        await message.reply("https://tenor.com/n1VZhJ8Bumt.gif")
    elif 'uwu' == message.content.lower():
        await message.reply("[UwU](https://files.mostwanted002.page/i_have_your_ip.mp4)")
    #    elif str(message.author.id) == '85614143951892480':
    #        await message.reply(["Chuppp bkl!! <:bahinchod:1076143675811319848>", "hhattt madarchod <:bahinchod:1076143675811319848>", "abeyy nikall lawde <:bahinchod:1076143675811319848>"][random.randint(0,2)])
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


@bot.event
async def on_member_join(member):
    await member.send(
        content="Welcome to the Indian PC Hardware Discord server!\nPlease go through the rules mentioned in <id:guide> and browse channles at <#1236943903693737994>.\n")


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
techpowerup = discord.SlashCommandGroup("techpowerup",
                                        "Provides with CPU and GPU specs and detailed spec links from Techpower Up database")


# CPU DB [/techpowerup cpu]
@techpowerup.command(description="Provides with CPU Specs and Detailed specs link")
async def cpu(
        ctx,
        brand: discord.Option(discord.SlashCommandOptionType.string, choices=["AMD", "Intel", "VIA"]),
        name: discord.Option(discord.SlashCommandOptionType.string,
                             description="Exact or part of the SKU to look for."),
        igpu: discord.Option(discord.SlashCommandOptionType.string, choices=["Yes", "No"], required=False,
                             description="Does it have an iGPU?", default=False),
        multiplier: discord.Option(discord.SlashCommandOptionType.string, choices=["Locked", "Unlocked"],
                                   required=False, description="Is the multiplier Locked or Unlocked?", default=False),
        class_of_cpu: discord.Option(discord.SlashCommandOptionType.string, required=False,
                                     choices=["Desktop", "Server", "Mobile", "Mobile Server"],
                                     description="Product Class of the CPU (Note: Only Intel has 'Mobile Server' class products.)",
                                     default=False)
):
    search_result = tpudb.searchcpu({
        "Brand": brand,
        "Name": name,
        "iGPU": igpu,
        "Product Class": class_of_cpu,
        "Multiplier": multiplier
    })
    if not search_result:
        await ctx.respond(f"No CPUs found with the name '{name}' under brand '{brand}' using your filters. Try again.")
    elif type(search_result) == tpudb.CPU:
        embedded_result = build_cpu_embed(search_result)
        await ctx.respond(f"We found the exact CPU!", embed=embedded_result)
    elif type(search_result) is list and len(search_result) < 25:
        await ctx.respond("Multiple CPUs found. Please pick one:",
                          view=CPUSelectorView(cpu_list=cpu_list_builder(search_result)))
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
    await ctx.respond(naming_scheme + "\n" + "https://files.mostwanted002.page/ryzen_mobile.jpg", ephemeral=True)


async def upload_files_async(paths):
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, upload_file, path)
            for path in tqdm(paths)
        ]
        return await asyncio.gather(*tasks)


@bot.command(description="Summarize the last x messages in the channel.")
async def summarize(ctx, message_count: int):
    # Check message count limit
    if message_count > 500:
        return await ctx.respond(
            "Can't summarize more than 500 messages at the moment. SuperEarth is working on XXXL Weapons Bay.",
            ephemeral=True)

    await ctx.response.defer(ephemeral=True)
    messages = await ctx.channel.history(limit=message_count + 1).flatten()
    messages = messages[1:]  # Exclude the command message itself

    # Create a JSON object with sender:message format
    message_data = []
    attachment_dir = f"attachments_{str(uuid.uuid4())}"

    if not os.path.exists(attachment_dir):
        os.makedirs(attachment_dir)

    for msg in messages:
        message_dict = {"sender": str(msg.author), "message": msg.content}

        if msg.attachments:
            message_dict["attachments"] = []
            for attachment in msg.attachments:
                if attachment.filename.lower().endswith(
                        tuple(allowed_media_types)):
                    file_path = os.path.join(attachment_dir, f"{str(uuid.uuid4())}_{attachment.filename}")

                    # Save the attachment
                    await attachment.save(file_path)

                    # Add watermark
                    if attachment.filename.lower().endswith(tuple(allowed_image_types)):
                        add_watermark(file_path, str(msg.author))

                    message_dict["attachments"].append(file_path)

        message_data.append(message_dict)
    # paths to all the attachments
    paths_attachment = glob.glob(f"{attachment_dir}/*")
    images_file_api = await upload_files_async(paths_attachment)

    for i in images_file_api:
        i = genai.get_file(i.name)
        while i.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(1)
            i = genai.get_file(i.name)
            print(i.state.name)

    message_json = json.dumps(message_data[::-1])
    model_choices = ['gemini-1.5-flash']
    model = genai.GenerativeModel(random.choice(model_choices), safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,

    })
    prompt = (f"Please summarize the following conversation.The following conversations might also include images."
              f"if given describe and summarize their role in the discord conversation too. If the conversation is long, please have an equally detailed summary:\n\n{message_json}.Please be descriptive and accurate in your summary.")
    full_prompt = [prompt] + images_file_api[:64]
    response = model.generate_content(full_prompt, )
    shutil.rmtree(attachment_dir)
    for i in images_file_api:
        genai.delete_file(i.name)
    try:
        summary = response.text
    except Exception as e:
        sys.stderr.buffer.write(f"Error: {e}".encode())
        if response.candidates:
            summary = "Unsafe message detected by the ministry of truth. Reporting to the nearest democracy officer.\nThe conversation contained a keyword that violated Gemini's safety ratings. Unfortunately, the exact keyword cannot be determined."
        else:
            summary = "Summarization failed due to unknown errors at Gemini."

    user = ctx.author
    try:
        try:
            await user.send(f"Here's a summary of the last {message_count} messages:\n\n{summary}\n\n"
                            f"Model Used for Summarization: {model.model_name.split('/')[-1]}\n\n"
                            "Please send any problems to the devs of this bot.\n")
        except:
            # Save summary to a text file
            summary_file_path = f"summary_{str(uuid.uuid4())}.txt"
            with open(summary_file_path, "w") as file:
                file.write(f"Here's a summary of the last {message_count} messages:\n\n{summary}\n\n")
                file.write(f"Model Used for Summarization: {model.model_name.split('/')[-1]}\n\n")
                file.write("Please send any problems to the devs of this bot.\n")

            # Send the text file as an attachment
            await user.send("The summary is too long to send directly. Please find the summary attached.",
                            file=discord.File(summary_file_path))
            os.remove(summary_file_path)  # Clean up the file after sending

        await ctx.respond("Summary sent as a direct message.", ephemeral=True)
    except discord.Forbidden:
        await ctx.respond(
            "I don't have permission to send you a direct message. Please enable direct messages from server members in your privacy settings.",
            ephemeral=True)


def add_watermark(image_path, sender):
    base = Image.open(image_path).convert('RGBA')
    width, height = base.size

    # Create a new image with extra space at the bottom
    new_height = height + 50  # Add 50 pixels for the black extension
    new_base = Image.new('RGBA', (width, new_height), (0, 0, 0, 255))
    new_base.paste(base, (0, 0))

    # Make the new image editable
    d = ImageDraw.Draw(new_base)

    # Choose a font and size
    font_size = 20
    try:
        fnt = ImageFont.truetype("arial.ttf",
                                 font_size)  # Ensure you have Arial font or replace with a path to a font file
    except IOError:
        fnt = ImageFont.load_default()

    # Position the text in the black extension
    text = f"Sent by: {sender}"
    bbox = d.textbbox((0, 0), text, font=fnt)
    textwidth = bbox[2] - bbox[0]
    textheight = bbox[3] - bbox[1]
    x = (width - textwidth) / 2
    y = height + (50 - textheight) / 2

    # Apply text to image
    d.text((x, y), text, font=fnt, fill=(255, 255, 255, 255))

    watermarked = new_base.convert('RGB')  # Remove alpha for saving in jpg format if needed
    watermarked.save(image_path)


bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
