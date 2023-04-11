import sys

import discord
from discord import app_commands, Interaction
from oi_discord_bot.config import *
from oi_discord_bot.utils import get_platform_info

sys.path.append("..")
from discord.ext import commands
import logging

logging.basicConfig(
    filename="oi.log",
    level=logging.DEBUG,
    format="%(asctime)s | %(name)s | %(levelname)s | %(" "message)s",
)
log = logging.getLogger(__name__)


class Utils(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(
        name="bot_info",
        description="get useful info about bot and the OS it's running on",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def unlater_leaderboard(self, interaction: Interaction):
        await interaction.response.defer()
        info_str = get_platform_info(self.client)
        await interaction.followup.send(content=info_str)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utils(bot))
