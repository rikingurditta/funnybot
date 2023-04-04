import sys

sys.path.append("..")
import datetime
import discord
import pytz
from apscheduler.triggers.date import DateTrigger
from discord import app_commands, Interaction, User
from discord.ext import commands
from oi_discord_bot.config import *
from oi_discord_bot.utils import get_role, remove_role, datetime_tz_str_to_datetime
from oi_discord_bot.onlyimages import tz
import logging

logging.basicConfig(format="%(message)s")
log = logging.getLogger(__name__)


class Later(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.scheduler = AsyncIOScheduler()

    @commands.Cog.listener()
    async def on_ready(self):
        # re-build scheduler with jobs from db lost when bot restarted
        jobs = db.get_all_later_deletion_jobs()
        for job in jobs:
            member_id = job[0]
            remove_time = datetime_tz_str_to_datetime(job[1])
            logging.warning(
                f"rebuilding later delete job for {member_id} at {remove_time}"
            )
            self.scheduler.add_job(
                self.remove_later_role,
                DateTrigger(run_date=remove_time),
                args=[member_id, str(remove_time)],
            )
        self.scheduler.start()
        log.warning("later jobs: " + str(self.scheduler.get_jobs()))

    @app_commands.command(
        name="later",
        description="later role",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.describe(
        hours="number of hours until role is removed",
    )
    async def later(
        self, interaction: Interaction, days: int = 0, hours: int = 0, minutes: int = 0
    ):
        await interaction.response.defer()
        if days < 0 or hours < 0 or minutes < 0:
            await interaction.followup.send("no negative numbers allowed!")
            return
        if days + hours + minutes == 0:
            await interaction.followup.send(
                "you must set a duration greater than zero!"
            )
            return
        user = interaction.user
        role = await get_role(self.client, LATER_ROLE_ID)
        try:
            if role in user.roles:
                await interaction.followup.send(
                    "you already have the later role! please wait until it is removed"
                )
                return
        except:
            log.warning("interaction returned User, not Member!")
        remove_time = tz.normalize(datetime.datetime.now(tz)).astimezone(
            pytz.utc
        ) + datetime.timedelta(days=days, hours=hours, minutes=minutes)

        # add role
        await user.add_roles(role, reason="later role requested by user")

        # schedule role removal
        await interaction.followup.send(
            "it's over. see you at {}".format(
                remove_time.replace(tzinfo=pytz.utc).astimezone(tz)
            )
        )
        self.scheduler.add_job(
            self.remove_later_role,
            DateTrigger(run_date=remove_time),
            args=[user.id, remove_time],
        )
        log.warning(str(self.scheduler.get_jobs()))
        db.create_later_delete_job(str(user.id), remove_time)

        # TODO: better followup message
        # TODO: scheduled role addition/removal every night/week night

    async def remove_later_role(self, user_id: int, remove_time):
        log.warning("removing later role for {}".format(user_id))
        await remove_role(self.client, LATER_ROLE_ID, user_id)
        db.delete_later_jobs_by_id(str(user_id))
        log.warning(str(self.scheduler.get_jobs()))

    @app_commands.command(
        name="unlater",
        description="Watch and pray that you may not enter into temptation. The spirit is willing, but the flesh is "
        "weak.",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    async def unlater(self, interaction: Interaction):
        await interaction.response.defer()
        user = interaction.user
        role = await get_role(self.client, LATER_ROLE_ID)
        if role in user.roles:
            await remove_role(self.client, LATER_ROLE_ID, user.id)
            await interaction.followup.send("we're back")
        else:
            await interaction.followup.send("you don't have the later role!")
        db.delete_later_jobs_by_id(str(user.id))
        db.update_unlater_count(str(user.id))

    @app_commands.command(
        name="unlaterleaderboard",
        description="leaderboard for times /unlater was called",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    async def unlater_leaderboard(self, interaction: Interaction):
        await interaction.response.defer()
        table = db.get_unlater_leaderboard()
        i = 1
        leaderboard = "/unlater leaderboard\n"
        unknown_users = []
        for row in table:
            try:
                user: User = self.client.get_user(row[0])
                if user is None:
                    user: User = await self.client.fetch_user(row[0])
            except:
                unknown_users.append(row[0])
                continue
            leaderboard += f"#{i:>3}: **{user.display_name}** - {row[1]} /unlaters\n"
            i += 1
        print(unknown_users)
        await interaction.followup.send(leaderboard)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Later(bot))
