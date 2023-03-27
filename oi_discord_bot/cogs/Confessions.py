import sys

sys.path.append("..")
import discord
from apscheduler.triggers.cron import CronTrigger
from discord import app_commands, Interaction, Embed, TextChannel
from discord.ext import commands
from oi_discord_bot.config import *


class Confessions(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        scheduler.add_job(
            self.post_confession, CronTrigger(hour="18", minute="0", second="0")
        )

    @app_commands.command(
        name="forceconfess",
        description="Force confession to be posted",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def force_confess(self, interaction: Interaction):
        await interaction.response.defer()
        rowid, confession = db.get_random_confession()
        if confession == "":
            await interaction.followup.send(content="no confessions")
        else:
            db.delete_confession(rowid)
            await interaction.followup.send(
                content="confession", embed=Embed(description=confession)
            )

    async def post_confession(self):
        rowid, confession = db.get_random_confession()
        if confession == "":
            return
        db.delete_confession(rowid)
        if confession != "":
            channel: TextChannel = await self.client.fetch_channel(
                CONFESSIONS_CHANNEL_ID
            )
            await channel.send(
                content="confession", embed=Embed(description=confession)
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Confessions(bot))
