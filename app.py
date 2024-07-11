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
import json
import glob
import shutil
from tqdm import tqdm
import uuid
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image, ImageDraw, ImageFont
import time
import threading

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
count = 0
last_author = ''
# DEBUG load_dotenv()

bot = discord.Bot(command_prefix='?_', intents=discord.Intents.all())

# Load large texts for commands from `command_texts.json`
commands_list = json.loads(open('command_texts.json', 'r').read())
commands_list = commands_list['commands']

## Definitions used by /summarize commands
allowed_image_types = ['png', 'jpg', 'jpeg', 'webp', ]
allowed_video_types = ['.mp4', '.mpeg', '.mov', '.avi', '.flv', '.mpg', '.webm', '.wmv', '.3gp']
allowed_media_types = allowed_image_types + allowed_video_types
model_choices = ['gemini-1.5-flash']
model = genai.GenerativeModel(random.choice(model_choices), safety_settings={
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,

})


## Utility function to get summary, called by /summarize
async def generate(prompt):
    return model.generate_content(prompt, )


## Utility function to parse messages and attachments to get summary for
async def get_summary(messages: list):
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
    images_file_api = []
    for path in tqdm(paths_attachment):
        images_file_api.append(genai.upload_file(path))
    for i in images_file_api:
        i = genai.get_file(i.name)
        while i.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(0.1)
            i = genai.get_file(i.name)
            print(i.state.name)

    message_json = json.dumps(message_data)

    prompt = (
        f"Please summarize the following conversation.The following conversations might also include images and other media"
        f"if given describe and summarize their role in the discord conversation too. If the conversation is long, please have an equally detailed summary:\n\n{message_json}.Please be descriptive and accurate in your summary.")
    full_prompt = [prompt] + images_file_api[:64]
    response = await generate(full_prompt)
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
    return summary


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


## All non-command interactions
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
        await message.reply(mentioned_me())
        count += 1
    elif '<@&1158756290261160016>' in message.content:
        await message.reply("https://tenor.com/n1VZhJ8Bumt.gif")
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
    # Send a direct message to the new member
    await member.send(
        content="S. if anyone with the role IPCHW janny dms you advertising a server called Indian PC hardware, ignore it")

    # Send a message to a welcome channel
    welcome_channel = member.guild.get_channel(
        1235520206760316972)  # Replace WELCOME_CHANNEL_ID with the actual channel ID
    if welcome_channel:
        await welcome_channel.send(f"Welcome to the server, {member.mention}!")




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
    await ctx.respond(commands_list['clearcmos']['content'])


## /vendors
@bot.command(descrption="Provides with the list of Trusted Online Vendors")
async def vendors(ctx):
    #    await ctx.respond("https://discord.com/channels/1039926726320468151/1240349211619360788/1241617373610643496")
    await ctx.respond(embed=vendor_list_embed(), ephemeral=True)


## /backupsolution
@bot.command(description="Provides with the link to UPS/Inverter Guide")
async def backupsolution(ctx):
    await ctx.respond("https://discord.com/channels/1039926726320468151/1123222529503416371")


## UV/OC command group
uvoc = discord.SlashCommandGroup("uvoc", "Undervolt and Overclocking guides.")

"""# undervolt
@uvoc.command(descrption="Provides with the guide to Undervolt your GPU/CPU")
async def undervolt(ctx):
    await ctx.respond("https://discord.com/channels/1039926726320468151/1111113878722596905")


# overclock
@uvoc.command(descrption="Provides with the guide to Overclock your GPU/CPU/Memory")
async def overclock(ctx):
    await undervolt(ctx)"""

bot.add_application_command(uvoc)


## Techpowerup Database commands


## /ryzenmobile
@bot.command(description="Naming scheme for Ryzen Mobile CPUs/APUs")
async def ryzenmobile(ctx):
    await ctx.respond(
        embed=create_embed("Naming scheme for Ryzen Mobile CPUs/APUs", commands_list['ryzenmobile']['content'],
                           commands_list['ryzenmobile']['image_url']), ephemeral=True)


## /summarize
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
    messages = messages[::-1]

    summary = await get_summary(messages)
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


## utility function to add watermark to attachment images
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


# /mark3d
@bot.command(description="Get 3D-Mark Download Links")
async def mark3d(ctx):
    await ctx.send_response(embed=create_embed("3D-Mark Download Links",
                                               "steam://install/231350\nhttps://store.steampowered.com/app/223850/3DMark/"))


# /aioorientation
@bot.command(description=commands_list['aioorientation']['description'])
async def aioorientation(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['aioorientation']['title'], commands_list['aioorientation']['content'],
                           commands_list['aioorientation']['image_url']))


# /airflow
@bot.command(description=commands_list['airflow']['description'])
async def airflow(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['airflow']['title'], "", commands_list['airflow']['image_url']))


# /biosupdate
@bot.command(description=commands_list['biosupdate']['description'])
async def biosupdate(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['biosupdate']['title'], commands_list['biosupdate']['content']))


# /bottleneck
@bot.command(description=commands_list['bottleneck']['description'])
async def bottleneck(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['bottleneck']['title'], commands_list['bottleneck']['content']))


# /brand
@bot.command(description="Brand vs Product")
async def brand(ctx):
    await ctx.send_response("""## Always buy by product, not by brand.
Every brand has good and bad products.""")


# /breadboarding
@bot.command(description=commands_list['breadboarding']['description'])
async def breadboarding(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['breadboarding']['title'], commands_list['breadboarding']['content']))


# /btheadset
@bot.command(description=commands_list['btheadset']['description'])
async def btheadset(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['btheadset']['title'], commands_list['btheadset']['content']))


# /buildask
@bot.command(description=commands_list['buildask']['description'])
async def buildask(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['buildask']['title'], commands_list['buildask']['content']))


# /casesata
@bot.command(description=commands_list['casesata']['description'])
async def casesata(ctx):
    await ctx.send_response(embed=create_embed(commands_list['casesata']['title'], commands_list['casesata']['content'],
                                               commands_list['ryzenmobile']['image_url']))


# /cat
@bot.command(description=commands_list['cat']['description'])
async def cat(ctx):
    await ctx.send_response(embed=create_embed(commands_list['cat']['title'], commands_list['cat']['content']))


# /cdi
@bot.command(description=commands_list['cdi']['description'])
async def cdi(ctx):
    await ctx.send_response(embed=create_embed(commands_list['cdi']['title'], commands_list['cdi']['content']))


# /cmrsmr
@bot.command(description=commands_list['cmrsmr']['description'])
async def cmrsmr(ctx):
    await ctx.send_response(embed=create_embed(commands_list['cmrsmr']['title'], commands_list['cmrsmr']['content']))


# /commonsense
@bot.command(description=commands_list['commonsense']['description'])
async def commonsense(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['commonsense']['title'], commands_list['commonsense']['content']))


# /cool
@bot.command(description="Cool.")
async def cool(ctx):
    await ctx.send_response(
        embed=create_embed("Cool.", "Cool.", "https://commands.discord.eegras.com//command_images/cool.jpg"))


# /cpuboost
@bot.command(description=commands_list['cpuboost']['description'])
async def cpuboost(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['cpuboost']['title'], commands_list['cpuboost']['content']))


# /cpuz
@bot.command(description=commands_list['cpuz']['description'])
async def cpuz(ctx):
    await ctx.send_response(embed=create_embed(commands_list['cpuz']['title'], commands_list['cpuz']['content']))


# /ddr
@bot.command(description=commands_list['ddr']['description'])
async def ddr(ctx):
    await ctx.send_response(embed=create_embed(commands_list['ddr']['title'], commands_list['ddr']['content']))


# /ddrjedec
@bot.command(description=commands_list['ddrjedec']['description'])
async def ddrjedec(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['ddrjedec']['title'], commands_list['ddrjedec']['content']))


# /dduhow
@bot.command(description=commands_list['dduhow']['description'])
async def dduhow(ctx):
    await ctx.send_response(embed=create_embed(commands_list['dduhow']['title'], commands_list['dduhow']['content']))


# /dns
@bot.command(description=commands_list['dns']['description'])
async def dns(ctx):
    await ctx.send_response(embed=create_embed(commands_list['dns']['title'], commands_list['dns']['content']))


# /dramssd
@bot.command(description=commands_list['dramssd']['description'])
async def dramssd(ctx):
    await ctx.send_response(embed=create_embed(commands_list['dramssd']['title'], commands_list['dramssd']['content']))


# /driveclone
@bot.command(description=commands_list['driveclone']['description'])
async def driveclone(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['driveclone']['title'], commands_list['driveclone']['content']))


# /driverupdater
@bot.command(description=commands_list['driverupdater']['description'])
async def driverupdater(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['driverupdater']['title'], commands_list['driverupdater']['content']))


# /drivespace
@bot.command(description=commands_list['drivespace']['description'])
async def drivespace(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['drivespace']['title'], commands_list['drivespace']['content']))


# /fanconnector
@bot.command(description=commands_list['fanconnector']['description'])
async def fanconnector(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['fanconnector']['title'], commands_list['fanconnector']['content'],
                           commands_list['fanconnector']['image_url']))


# /fandaisychain
@bot.command(description=commands_list['fandaisychain']['description'])
async def fandaisychain(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['fandaisychain']['title'], commands_list['fandaisychain']['content'],
                           commands_list['fandaisychain']['image_url']))


# /fanorientation
@bot.command(description=commands_list['fanorientation']['description'])
async def fanorientation(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['fanorientation']['title'], commands_list['fanorientation']['content'],
                           commands_list['fanorientation']['image_url']))


# /fantable
@bot.command(description=commands_list['fantable']['description'])
async def fantable(ctx):
    await ctx.send_response(embed=create_embed(commands_list['fantable']['title'], commands_list['fantable']['content'],
                                               commands_list['fantable']['image_url']))


# /firstdrivers
@bot.command(description=commands_list['firstdrivers']['description'])
async def firstdrivers(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['firstdrivers']['title'], commands_list['firstdrivers']['content']))


# /fpanel
@bot.command(description=commands_list['fpanel']['description'])
async def fpanel(ctx):
    await ctx.send_response(embed=create_embed(commands_list['fpanel']['title'], commands_list['fpanel']['content'],
                                               commands_list['fpanel']['image_url']))


# /freedomofspeech
@bot.command(description=commands_list['freedomofspeech']['description'])
async def freedomofspeech(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['freedomofspeech']['title'], commands_list['freedomofspeech']['content'],
                           commands_list['freedomofspeech']['image_url']))


# /gptmbr
@bot.command(description=commands_list['gptmbr']['description'])
async def gptmbr(ctx):
    await ctx.send_response(embed=create_embed(commands_list['gptmbr']['title'], commands_list['gptmbr']['content']))


# /headsetmic
@bot.command(description=commands_list['headsetmic']['description'])
async def headsetmic(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['headsetmic']['title'], commands_list['headsetmic']['content'],
                           commands_list['headsetmic']['image_url']))


# /highmonitor
@bot.command(description=commands_list['highmonitor']['description'])
async def highmonitor(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['highmonitor']['title'], commands_list['highmonitor']['content']))


# /hwinfo
@bot.command(description=commands_list['hwinfo']['description'])
async def hwinfo(ctx):
    await ctx.send_response(embed=create_embed(commands_list['hwinfo']['title'], commands_list['hwinfo']['content']))


# /idletemp
@bot.command(description=commands_list['idletemp']['description'])
async def idletemp(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['idletemp']['title'], commands_list['idletemp']['content']))


# /justask
@bot.command(description=commands_list['justask']['description'])
async def justask(ctx):
    await ctx.send_response(embed=create_embed(commands_list['justask']['title'], commands_list['justask']['content']))


# /keyboardsize
@bot.command(description=commands_list['keyboardsize']['description'])
async def keyboardsize(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['keyboardsize']['title'], commands_list['keyboardsize']['content'],
                           commands_list['keyboardsize']['image_url']))


# /m2install
@bot.command(description=commands_list['m2install']['description'])
async def m2install(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['m2install']['title'], commands_list['m2install']['content'],
                           commands_list['m2install']['image_url']))


# /m2sizes
@bot.command(description=commands_list['m2sizes']['description'])
async def m2sizes(ctx):
    await ctx.send_response(embed=create_embed(commands_list['m2sizes']['title'], commands_list['m2sizes']['content'],
                                               commands_list['m2sizes']['image_url']))


# /manual
@bot.command(description=commands_list['manual']['description'])
async def manual(ctx):
    await ctx.send_response(embed=create_embed(commands_list['manual']['title'], commands_list['manual']['content']))


# /mbguide
@bot.command(description=commands_list['mbguide']['description'])
async def mbguide(ctx):
    await ctx.send_response(embed=create_embed(commands_list['mbguide']['title'], commands_list['mbguide']['content'],
                                               commands_list['mbguide']['image_url']))


# /mbr2gpt
@bot.command(description=commands_list['mbr2gpt']['description'])
async def mbr2gpt(ctx):
    await ctx.send_response(embed=create_embed(commands_list['mbr2gpt']['title'], commands_list['mbr2gpt']['content']))


# /memtest
@bot.command(description=commands_list['memtest']['description'])
async def memtest(ctx):
    await ctx.send_response(embed=create_embed(commands_list['memtest']['title'], commands_list['memtest']['content']))


# /modular
@bot.command(description=commands_list['modular']['description'])
async def modular(ctx):
    await ctx.send_response(embed=create_embed(commands_list['modular']['title'], commands_list['modular']['content'],
                                               commands_list['modular']['image_url']))


# /motherboardsize
@bot.command(description=commands_list['motherboardsize']['description'])
async def motherboardsize(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['motherboardsize']['title'], commands_list['motherboardsize']['content'],
                           commands_list['motherboardsize']['image_url']))


# /netreset
@bot.command(description=commands_list['netreset']['description'])
async def netreset(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['netreset']['title'], commands_list['netreset']['content']))


# /networkhelp
@bot.command(description=commands_list['networkhelp']['description'])
async def networkhelp(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['networkhelp']['title'], commands_list['networkhelp']['content']))


# /networking
@bot.command(description=commands_list['networking']['description'])
async def networking(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['networking']['title'], commands_list['networking']['content'],
                           commands_list['networking']['image_url']))


# /nodisplay
@bot.command(description=commands_list['nodisplay']['description'])
async def nodisplay(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['nodisplay']['title'], commands_list['nodisplay']['content'],
                           commands_list['nodisplay']['image_url']))


# /nvmesata
@bot.command(description=commands_list['nvmesata']['description'])
async def nvmesata(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['nvmesata']['title'], commands_list['nvmesata']['content']))


# /occt
@bot.command(description=commands_list['occt']['description'])
async def occt(ctx):
    await ctx.send_response(embed=create_embed(commands_list['occt']['title'], commands_list['occt']['content']))


# /opinion
@bot.command(description=commands_list['opinion']['description'])
async def opinion(ctx):
    await ctx.send_response(embed=create_embed(commands_list['opinion']['title'], commands_list['opinion']['content']))


# /pcbuildtroubleshoot
@bot.command(description=commands_list['pcbuildtroubleshoot']['description'])
async def pcbuildtroubleshoot(ctx):
    await ctx.send_response(embed=create_embed(commands_list['pcbuildtroubleshoot']['title'],
                                               commands_list['pcbuildtroubleshoot']['content'],
                                               commands_list['pcbuildtroubleshoot']['image_url']))


# /pcielock
@bot.command(description=commands_list['pcielock']['description'])
async def pcielock(ctx):
    await ctx.send_response(embed=create_embed(commands_list['pcielock']['title'], commands_list['pcielock']['content'],
                                               commands_list['pcielock']['image_url']))


# /pciepower
@bot.command(description=commands_list['pciepower']['description'])
async def pciepower(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['pciepower']['title'], commands_list['pciepower']['content'],
                           commands_list['pciepower']['image_url']))


# /pcieslots
@bot.command(description=commands_list['pcieslots']['description'])
async def pcieslots(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['pcieslots']['title'], commands_list['pcieslots']['content'],
                           commands_list['pcieslots']['image_url']))


# /psucabletypes
@bot.command(description=commands_list['psucabletypes']['description'])
async def psucabletypes(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['psucabletypes']['title'], commands_list['psucabletypes']['content'],
                           commands_list['psucabletypes']['image_url']))


# /pushpull
@bot.command(description=commands_list['pushpull']['description'])
async def pushpull(ctx):
    await ctx.send_response(embed=create_embed(commands_list['pushpull']['title'], commands_list['pushpull']['content'],
                                               commands_list['pushpull']['image_url']))


# /qvl
@bot.command(description=commands_list['qvl']['description'])
async def qvl(ctx):
    await ctx.send_response(embed=create_embed(commands_list['qvl']['title'], commands_list['qvl']['content']))


# /raid
@bot.command(description=commands_list['raid']['description'])
async def raid(ctx):
    await ctx.send_response(embed=create_embed(commands_list['raid']['title'], commands_list['raid']['content']))


# /randomrestart
@bot.command(description=commands_list['randomrestart']['description'])
async def randomrestart(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['randomrestart']['title'], commands_list['randomrestart']['content']))


# /rgbconnector
@bot.command(description=commands_list['rgbconnector']['description'])
async def rgbconnector(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['rgbconnector']['title'], commands_list['rgbconnector']['content'],
                           commands_list['rgbconnector']['image_url']))


# /rgbconnectortype
@bot.command(description=commands_list['rgbconnectortype']['description'])
async def rgbconnectortype(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['rgbconnectortype']['title'], commands_list['rgbconnectortype']['content'],
                           commands_list['rgbconnectortype']['image_url']))


# /rgbcontrol
@bot.command(description=commands_list['rgbcontrol']['description'])
async def rgbcontrol(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['rgbcontrol']['title'], commands_list['rgbcontrol']['content']))


# /rtfm
@bot.command(description=commands_list['rtfm']['description'])
async def rtfm(ctx):
    await ctx.send_response(embed=create_embed(commands_list['rtfm']['title'], commands_list['rtfm']['content'],
                                               commands_list['rtfm']['image_url']))


# /sataconnection
@bot.command(description=commands_list['sataconnection']['description'])
async def sataconnection(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['sataconnection']['title'], commands_list['sataconnection']['content'],
                           commands_list['sataconnection']['image_url']))


# /smart
@bot.command(description=commands_list['smart']['description'])
async def smart(ctx):
    await ctx.send_response(embed=create_embed(commands_list['smart']['title'], commands_list['smart']['content'],
                                               commands_list['smart']['image_url']))


# /smfail
@bot.command(description=commands_list['smfail']['description'])
async def smfail(ctx):
    await ctx.send_response(embed=create_embed(commands_list['smfail']['title'], commands_list['smfail']['content'],
                                               commands_list['smfail']['image_url']))


# /smnormal
@bot.command(description=commands_list['smnormal']['description'])
async def smnormal(ctx):
    await ctx.send_response(embed=create_embed(commands_list['smnormal']['title'], commands_list['smnormal']['content'],
                                               commands_list['smnormal']['image_url']))


# /ssdtypes
@bot.command(description=commands_list['ssdtypes']['description'])
async def ssdtypes(ctx):
    await ctx.send_response(embed=create_embed(commands_list['ssdtypes']['title'], commands_list['ssdtypes']['content'],
                                               commands_list['ssdtypes']['image_url']))


# /stfu
@bot.command(description=commands_list['stfu']['description'])
async def stfu(ctx):
    await ctx.send_response(embed=create_embed(commands_list['stfu']['title'], commands_list['stfu']['content'],
                                               commands_list['stfu']['image_url']))


# /supportchannels
@bot.command(description=commands_list['supportchannels']['description'])
async def supportchannels(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['supportchannels']['title'], commands_list['supportchannels']['content'],
                           commands_list['supportchannels']['image_url']))


# /temps
@bot.command(description=commands_list['temps']['description'])
async def temps(ctx):
    await ctx.send_response(embed=create_embed(commands_list['temps']['title'], commands_list['temps']['content'],
                                               commands_list['temps']['image_url']))


# /usbc
@bot.command(description=commands_list['usbc']['description'])
async def usbc(ctx):
    await ctx.send_response(embed=create_embed(commands_list['usbc']['title'], commands_list['usbc']['content'],
                                               commands_list['usbc']['image_url']))


# /usbtypes
@bot.command(description=commands_list['usbtypes']['description'])
async def usbtypes(ctx):
    await ctx.send_response(embed=create_embed(commands_list['usbtypes']['title'], commands_list['usbtypes']['content'],
                                               commands_list['usbtypes']['image_url']))


# /userbenchmark
@bot.command(description=commands_list['userbenchmark']['description'])
async def userbenchmark(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['userbenchmark']['title'], commands_list['userbenchmark']['content'],
                           commands_list['userbenchmark']['image_url']))


# /w11
@bot.command(description=commands_list['w11']['description'])
async def w11(ctx):
    await ctx.send_response(embed=create_embed(commands_list['w11']['title'], commands_list['w11']['content'],
                                               commands_list['w11']['image_url']))


# /w11installbypass
@bot.command(description=commands_list['w11installbypass']['description'])
async def w11installbypass(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['w11installbypass']['title'], commands_list['w11installbypass']['content'],
                           commands_list['w11installbypass']['image_url']))


# /whackamole
@bot.command(description=commands_list['whackamole']['description'])
async def whackamole(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['whackamole']['title'], commands_list['whackamole']['content'],
                           commands_list['whackamole']['image_url']))


# /whatsm2
@bot.command(description=commands_list['whatsm2']['description'])
async def whatsm2(ctx):
    await ctx.send_response(embed=create_embed(commands_list['whatsm2']['title'], commands_list['whatsm2']['content'],
                                               commands_list['whatsm2']['image_url']))


# /wic
@bot.command(description=commands_list['wic']['description'])
async def wic(ctx):
    await ctx.send_response(embed=create_embed(commands_list['wic']['title'], commands_list['wic']['content'],
                                               commands_list['wic']['image_url']))


# /windowsreinstall
@bot.command(description=commands_list['windowsreinstall']['description'])
async def windowsreinstall(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['windowsreinstall']['title'], commands_list['windowsreinstall']['content'],
                           commands_list['windowsreinstall']['image_url']))


# /xmp
@bot.command(description=commands_list['xmp']['description'])
async def xmp(ctx):
    await ctx.send_response(embed=create_embed(commands_list['xmp']['title'], commands_list['xmp']['content'],
                                               commands_list['xmp']['image_url']))


# /xmpfix
@bot.command(description=commands_list['xmpfix']['description'])
async def xmpfix(ctx):
    await ctx.send_response(embed=create_embed(commands_list['xmpfix']['title'], commands_list['xmpfix']['content'],
                                               commands_list['xmpfix']['image_url']))


# /xyproblem
@bot.command(description=commands_list['xyproblem']['description'])
async def xyproblem(ctx):
    await ctx.send_response(
        embed=create_embed(commands_list['xyproblem']['title'], commands_list['xyproblem']['content'],
                           commands_list['xyproblem']['image_url']))


bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
