from discord import Embed, Color, ui, SelectOption
from discord.components import SelectOption
from discord.enums import ChannelType, ComponentType
from discord.interactions import Interaction
from discord.ui.item import Item
from techpowerup import *
import random


class CPUDropdown(ui.Select):
    def __init__(self, cpu_list: list) -> None:
        self.options_list = []
        self.mapped_options = {}
        for cpu in cpu_list:
            self.mapped_options.update({f"{cpu.name}": cpu})
            self.options_list.append(SelectOption(
                label=cpu.name,
                description=f"Released in {cpu.released}"
            ))
        super().__init__(
            placeholder="Following CPUs were found for your query", 
            min_values=1,
            max_values=1,
            options=self.options_list
            )
        
    async def callback(self, interaction: Interaction):
        await interaction.response.edit_message(content="Here is specs for selected CPU", embed=build_cpu_embed(cpu=self.mapped_options[self.values[0]]))
        
        
class CPUSelectorView(ui.View):
    def __init__(self, cpu_list: list, *items: Item, timeout=30, disable_on_timeout=True):
        self.cpu_list = cpu_list
        super().__init__(timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.add_item(CPUDropdown(self.cpu_list))

    async def on_timeout(self):
        self.clear_items()
        return await super().on_timeout()




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
    embed.add_field(name="Processor Class", value=cpu.product_class, inline=True)
    embed.add_field(name="Cores", value=cpu.cores, inline=True)
    embed.add_field(name="Clock", value=cpu.clock, inline=True)
    embed.add_field(name="Socket", value=cpu.socket, inline=True)
    embed.add_field(name="Process", value=cpu.process, inline=True)
    embed.add_field(name="L3 Cache", value=cpu.l3cache, inline=True)
    embed.add_field(name="TDP", value=cpu.tdp, inline=True)
    embed.add_field(name="iGPU", value=cpu.igpu, inline=True)
    embed.add_field(name="Multiplier", value=cpu.multiplier, inline=True)
    embed.add_field(name="Link", value=f"[Detailed Specs on Techpowerup](https://techpowerup.com{cpu.link})")

    embed.set_author(name="IPCHW Bot", icon_url='https://i.imgur.com/tLkVAlI.png')
    return embed


def cpu_list_builder(cpu_list: list):
    cpuList = [CPU(cpu) for cpu in cpu_list]
    return cpuList


def check_soy(message_content: str):
    soy_keywords = ['soy', 'soyjack', 'goyim', 'slop', 'suuure', '1984', 'cum', 'lodu', 'lund', 'cringe', 'cope', 'liberal']
    for keyword in soy_keywords:
        if keyword in message_content:
            return True
    return False

def mentioned_me():
    memes = [
        "<:bahinchod:1076143675811319848>",
        "[ honestly..., ](https://video.twimg.com/ext_tw_video/1693802046971875328/pu/vid/1280x720/9kXFQO_uea4CcUnH.mp4)",
        "[ you know what...](https://files.mostwanted002.page/debates%20like%20a%20redittor.mp4)",
        "<:soy:1142126551484338248> [LoOk aT mE](https://files.mostwanted002.page/hype_train.mp4)",
        "[fr fr ong no cap](https://files.mostwanted002.page/acoustic.mp4)",
        "[THE CONTENT!!!](https://files.mostwanted002.page/content_is_fire.mp4)",
        "[despair...](https://files.mostwanted002.page/when_will_it_end.mp4)",
        "[UwU](https://files.mostwanted002.page/i_have_your_ip.mp4)"
        ]
    dice = random.randint(0, 100000) % len(memes)
    return(memes[dice])