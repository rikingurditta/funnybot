import sys

sys.path.append("..")
import datetime
import discord
import pytz
from apscheduler.triggers.date import DateTrigger
from discord import app_commands, Interaction
from discord.ext import commands
from oi_discord_bot.config import *
from oi_discord_bot.utils import get_role, remove_role
from oi_discord_bot.onlyimages import tree, tz


class Later(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @tree.command(
        name="later",
        description="later role",
        guild=discord.Object(id=OI_GUILD_ID),
    )
    @app_commands.describe(
        hours="number of hours until role is removed",
    )
    async def later(self, interaction: Interaction, days: int, hours: int):
        await interaction.response.defer()
        user = interaction.user
        role = await get_role(self.client, LATER_ROLE_ID)
        remove_time = tz.normalize(datetime.datetime.now(tz)).astimezone(
            pytz.utc
        ) + datetime.timedelta(days=days, hours=hours)

        # add role
        await user.add_roles(role, reason="role added by oi_discord_bot")

        # schedule role removal
        await interaction.followup.send("later!")
        scheduler.add_job(
            remove_role, DateTrigger(run_date=remove_time), args=[user, role]
        )

        # TODO: better followup message
        # TODO: store the roles/times in backup
        # TODO: scheduled role addition/removal every night/week night


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Later(bot))
