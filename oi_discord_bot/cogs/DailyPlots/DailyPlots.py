import discord
from discord import TextChannel, app_commands, Interaction
from discord.ext import commands
from oi_discord_bot.config import *
from .oi_daily_plot_functions import make_daily_graph
import logging

logging.basicConfig(filename='oi.log', level=logging.DEBUG, format='%(asctime)s | %(name)s | %(levelname)s | %('
                                                                   'message)s')
log = logging.getLogger(__name__)


class DailyPlots(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.scheduler = AsyncIOScheduler()

    @commands.Cog.listener()
    async def on_ready(self):
        # scheduler.add_job(post_plot_job, CronTrigger(hour="12", minute="0", second="0"))
        # self.scheduler.start()
        # log.warning("dailyplot jobs: " + str(self.scheduler.get_jobs()))
        pass

    async def post_plot_job(self):
        make_daily_graph("cogs/DailyPlots/oi_responses.csv", "cogs/DailyPlots/oi_biases.tsv")
        channel: TextChannel = self.client.get_channel(GENERAL_CHANNEL_ID)
        if channel is None:
            channel: TextChannel = await self.client.fetch_channel(GENERAL_CHANNEL_ID)
        await channel.send(file=discord.File("dailygraph.png"))

    @app_commands.command(
        name="forceplot",
        description="Requires OI bot dev role - Force rose's daily plot to be posted",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def force_run_daily_plot(self, interaction: Interaction):
        await interaction.response.defer()
        make_daily_graph(
            "cogs/DailyPlots/oi_responses.csv", "cogs/DailyPlots/oi_biases.tsv"
        )
        await interaction.followup.send(file=discord.File("dailygraph.png"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DailyPlots(bot))
