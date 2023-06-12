from discord import Embed, Color, ui, SelectOption
from discord.components import SelectOption
from discord.enums import ChannelType, ComponentType
from discord.interactions import Interaction
from discord.ui.item import Item
from techpowerup import *



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
    embed.add_field(name="Cores", value=cpu.cores, inline=True)
    embed.add_field(name="Clock", value=cpu.clock, inline=True)
    embed.add_field(name="Socket", value=cpu.socket, inline=True)
    embed.add_field(name="Process", value=cpu.process, inline=True)
    embed.add_field(name="L3 Cache", value=cpu.l3cache, inline=True)
    embed.add_field(name="TDP", value=cpu.tdp, inline=True)
    embed.add_field(name="Link", value=f"[Detailed Specs on Techpowerup](https://techpowerup.com{cpu.link})")
    
    embed.set_author(name="IPCHW Bot", icon_url='https://i.imgur.com/tLkVAlI.png')
    return embed


def cpu_list_builder(cpu_list: list):
    cpuList = [CPU(cpu) for cpu in cpu_list]
    return cpuList