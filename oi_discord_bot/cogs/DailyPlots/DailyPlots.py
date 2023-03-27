import sys
sys.path.append("..")
import discord
from discord import TextChannel, app_commands, Interaction
from discord.ext import commands
from oi_discord_bot.config import *
from oi_discord_bot.onlyimages import tree
from oi_daily_plot_functions import make_daily_graph



class DailyPlots(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        # scheduler.add_job(post_plot_job, CronTrigger(hour="12", minute="0", second="0"))
        pass

    async def post_plot_job(self):
        make_daily_graph("oi_responses.csv", "oi_biases.tsv")
        channel: TextChannel = self.client.get_channel(GENERAL_CHANNEL_ID)
        if channel is None:
            channel: TextChannel = await self.client.fetch_channel(GENERAL_CHANNEL_ID)
        await channel.send(file=discord.File("dailygraph.png"))

    @tree.command(
        name="forceplot",
        description="Force rose's daily plot to be posted",
        guild=discord.Object(id=OI_GUILD_ID),
    )
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def force_run_daily_plot(self, interaction: Interaction):
        await interaction.response.defer()
        make_daily_graph(
            "../daily_plots/oi_responses.csv", "../daily_plots/oi_biases.tsv"
        )
        await interaction.followup.send(file=discord.File("dailygraph.png"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DailyPlots(bot))
