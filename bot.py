import os
import re
import discord
from discord import app_commands
from discord.ext import commands

# Gets token securely from the hosting 
BOT_TOKEN = os.getenv( "MTMxNDY1MTA1NDUyMDEzOTc5Nw.GQRFny.pxXmAKswpQdsbko39j8FTofpUVQBPIIVqLLM0s" )

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
CONFIG = {}

class ChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Select the input channel...",
            channel_types=[discord.ChannelType.text]
        )

    async def callback(self, interaction: discord.Interaction):
        selected_channel = self.values[0]
        CONFIG[interaction.guild_id] = selected_channel.id
        await interaction.response.send_message(
            f"✅ Input channel set to {selected_channel.mention}.",
            ephemeral=True
        )

class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(ChannelSelect())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot logged in as {bot.user.name}")

@bot.tree.command(name="setup", description="Select input channel")
@app_commands.default_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Select your announcement channel:",
        view=SetupView(),
        ephemeral=True
    )

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    configured_channel_id = CONFIG.get(message.guild.id)
    if configured_channel_id and message.channel.id == configured_channel_id:
        pattern = r"End:\s*<#(\d+)>\s*$"
        match = re.search(pattern, message.content, re.IGNORECASE)

        if match:
            target_channel_id = int(match.group(1))
            target_channel = bot.get_channel(target_channel_id)

            if target_channel:
                announcement_text = re.sub(pattern, "", message.content, flags=re.IGNORECASE).strip()
                try:
                    await target_channel.send(announcement_text)
                    await message.add_reaction("✅")
                except Exception as e:
                    await message.channel.send(f"⚠️ Error: {e}")

    await bot.process_commands(message)

bot.run(BOT_TOKEN)

