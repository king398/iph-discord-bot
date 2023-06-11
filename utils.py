from discord import Embed, Color
from techpowerup import *

def build_cpu_embed(cpu : CPU):
    color = Color.light_grey()
    if cpu.brand == "AMD":
        color = Color.red()
    if cpu.brand == "Intel":
        color = Color.blue()
    embed = Embed(
        title=f"{cpu.name} by {cpu.brand}",
        description=f"Released : {cpu.released}",
        color=color
    )
    embed.add_field(name="Codename", value=cpu.codename, inline=True)
    embed.add_field(name="Cores", value=cpu.cores, inline=True)
    embed.add_field(name="Clock", value=cpu.clock, inline=True)
    embed.add_field(name="Socket", value=cpu.socket, inline=True)
    embed.add_field(name="Process", value=cpu.process, inline=True)
    embed.add_field(name="L3 Cache", value=cpu.l3cache, inline=True)
    embed.add_field(name="TDP", value=cpu.tdp, inline=True)
    embed.add_field(name="Link", value=f"[Detailed Specs on Techpowerup](https://techpowerup.com{cpu.link})")
    
    embed.set_author(name="IPCHW Bot", icon_url='https://i.imgur.com/tLkVAlI.png')
    return embed