import sys

import discord
from discord import app_commands, Interaction
from oi_discord_bot.config import *
from oi_discord_bot.utils import get_platform_info, read_oi_log

sys.path.append("..")
from discord.ext import commands
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(" "message)s",
    handlers=[logging.FileHandler("oi.log"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Utils(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(
        name="bot_info",
        description="get useful info about bot and the OS it's running on",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def get_info(self, interaction: Interaction):
        await interaction.response.defer()
        info_str = get_platform_info(self.client)
        await interaction.followup.send(content=info_str)

    @app_commands.command(
        name="get_logs",
        description="get last lines of bot log file",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def get_logs(self, interaction: Interaction, lines: int = 20):
        await interaction.response.defer()
        info_str = "```prolog\n" + read_oi_log(lines) + "\n```"
        await interaction.followup.send(content=info_str)

    @app_commands.command(
        name="insert_word",
        description="insert word and definition into custom hangman db",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def insert_word(self, interaction: Interaction, word: str, definition: str):
        await interaction.response.defer()
        ret = db.insert_new_word(word, definition)
        if ret:
            await interaction.followup.send(content=f"Inserted {word} into db with definition {definition}.")
        else:
            await interaction.followup.send(content=f"Failed to insert {word} into db (word already exists).")

    @app_commands.command(
        name="delete_word",
        description="delete word from custom hangman db",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def delete_word(self, interaction: Interaction, word: str):
        await interaction.response.defer()
        db.remove_word(word)
        await interaction.followup.send(content=f"Deleted {word} from db.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utils(bot))
