import sys

sys.path.append("..")
import discord
from apscheduler.triggers.cron import CronTrigger
from discord import Interaction, app_commands, TextChannel, Embed
from discord.ext import commands
from oi_discord_bot.config import *
import logging

logging.basicConfig(format="%(message)s")
log = logging.getLogger(__name__)


class WYR(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.scheduler = AsyncIOScheduler()

    @commands.Cog.listener()
    async def on_ready(self):
        self.scheduler.add_job(self.post_wyr, CronTrigger(hour="12", minute="0", second="0"))
        self.scheduler.start()
        log.warning("wyr jobs: " + str(self.scheduler.get_jobs()))

    @app_commands.command(
        name="forcewyr",
        description="Force WYR to be posted",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def force_wyr(self, interaction: Interaction):
        await interaction.response.defer()
        rowid, wyr = db.get_random_wyr()
        if wyr == "":
            await interaction.followup.send(content="no options")
        else:
            db.delete_wyr(rowid)
            message = await interaction.followup.send(
                content="Would you rather", embed=Embed(description=wyr)
            )
            for emoji in WYR_EMOJIS:
                await message.add_reaction(emoji)

    async def post_wyr(self):
        rowid, wyr = db.get_random_wyr()
        if wyr == "":
            return
        db.delete_wyr(rowid)
        if wyr != "":
            channel: TextChannel = await self.client.fetch_channel(WYR_CHANNEL_ID)
            message = await channel.send(
                content="Would you rather", embed=Embed(description=wyr)
            )
            for emoji in WYR_EMOJIS:
                await message.add_reaction(emoji)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WYR(bot))
