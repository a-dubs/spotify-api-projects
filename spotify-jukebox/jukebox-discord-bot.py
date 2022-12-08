from discord import channel
import requests
import discord
from discord.ext import commands 
from datetime import datetime
import time
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

bot_token = ""
bot = discord.Client(command_prefix=".",intents=discord.Intents(messages=True, guilds=True))
bot_id = 0

SADIESPOT_SERVER_ID = 1004384217670627409
DISCORD_TESTING_CHANNEL_ID = 1004384316127727706



class Jukebox_Main_Menu(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label="Minecraft Server Controls",style=discord.ButtonStyle.green, row=0, emoji="<a:steve_dance:978321220862889984>")
    async def gray_button(self,interaction:discord.Interaction, button:discord.ui.Button):
        button.style=discord.ButtonStyle.green
        await interaction.response.edit_message(content=f"**Select Target Server/World**:", view=MCServers_Select_Buttons())
    


class MCServers_Select_Buttons(discord.ui.View):
    def __init__(self, *, timeout=86400):
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label="Surivival",style=discord.ButtonStyle.grey, row=0, emoji="<a:portalMinecraft:840155297285013524>")
    async def survival_button(self,interaction:discord.Interaction, button:discord.ui.Button):
        button.style=discord.ButtonStyle.green
        await interaction.response.edit_message(content=f"\"**Survival\" World**:\n" + stringify_mcserver_status(get_mcserver_status("survival")), view=MCServers_Control_Buttons(selected_server="survival"))
    
    @discord.ui.button(label="Creative",style=discord.ButtonStyle.grey, row=0, emoji="<a:minecraftbirdhype:772709667256139786>")
    async def creative_button(self,interaction:discord.Interaction, button:discord.ui.Button):
        button.style=discord.ButtonStyle.green
        await interaction.response.edit_message(content=f"\"**Creative Building & Design\" World**:\n" + stringify_mcserver_status(get_mcserver_status("creative")), view=MCServers_Control_Buttons(selected_server="creative"))
    
    @discord.ui.button(label="Exploring",style=discord.ButtonStyle.grey, row=0, emoji="<a:spinning_steve:978321127346696312>")
    async def exploring_button(self,interaction:discord.Interaction, button:discord.ui.Button):
        button.style=discord.ButtonStyle.green
        await interaction.response.edit_message(content=f"\"**Exploring Surival Seed\" World**:\n"  + stringify_mcserver_status(get_mcserver_status("exploring")), view=MCServers_Control_Buttons(selected_server="exploring"))
