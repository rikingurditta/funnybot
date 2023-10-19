import sys

sys.path.append("..")
import datetime
import discord
import pytz
from apscheduler.triggers.date import DateTrigger
from discord import app_commands, Interaction, User
from discord.ext import commands
from oi_discord_bot.config import *
from oi_discord_bot.oi_utils import get_role, remove_role, datetime_tz_str_to_datetime
from oi_discord_bot.onlyimages import tz
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(" "message)s",
    handlers=[logging.FileHandler("oi.log"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def update_later_min_lb(id):
    latered_time = db.get_last_later_time(id)
    latered_time = datetime_tz_str_to_datetime(latered_time)
    now = tz.normalize(datetime.datetime.now(tz)).astimezone(pytz.utc)
    diff_min = (now - latered_time).total_seconds() / 60
    db.update_later_min_count(id, int(diff_min))
    db.remove_later_time(id)


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
            logging.info(
                f"rebuilding later delete job for {member_id} at {remove_time}"
            )
            ret_job = self.scheduler.add_job(
                self.remove_later_role,
                DateTrigger(run_date=remove_time),
                args=[member_id, str(remove_time)],
            )
            latermin_entry = db.get_last_later_time(member_id)
            if latermin_entry is None:
                db.insert_later_time(
                    member_id,
                    str(tz.normalize(datetime.datetime.now(tz)).astimezone(pytz.utc)),
                )

            # updates later deletion job with apscheduler job id
            db.create_later_delete_job(job[0], job[1], ret_job.id)
        self.scheduler.start()
        log.info("later jobs: " + str(self.scheduler.get_jobs()))

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
        now = tz.normalize(datetime.datetime.now(tz)).astimezone(pytz.utc)
        remove_time = now + datetime.timedelta(days=days, hours=hours, minutes=minutes)
        db.insert_later_time(str(user.id), str(now))

        # add role
        await user.add_roles(role, reason="later role requested by user")

        # schedule role removal
        await interaction.followup.send(
            "it's over. see you at {}".format(
                remove_time.replace(tzinfo=pytz.utc).astimezone(tz)
            )
        )
        ret_job = self.scheduler.add_job(
            self.remove_later_role,
            DateTrigger(run_date=remove_time),
            args=[user.id, remove_time],
        )
        log.info(str(self.scheduler.get_jobs()))
        db.create_later_delete_job(str(user.id), remove_time, ret_job.id)

        # TODO: better followup message
        # TODO: scheduled role addition/removal every night/week night

    async def remove_later_role(self, user_id: int, remove_time):
        log.info("removing later role for {}".format(user_id))
        await remove_role(self.client, LATER_ROLE_ID, user_id)
        jobs = db.get_later_deletion_jobs_by_id(str(user_id))
        for job in jobs:
            try:
                log.info("removing job: " + str(job[2]))
                self.scheduler.remove_job(job[2])
            except Exception as e:
                log.warning(e)
        db.delete_later_jobs_by_id(str(user_id))
        update_later_min_lb(str(user_id))
        log.info(str(self.scheduler.get_jobs()))

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
            db.update_unlater_count(str(user.id))
        else:
            await interaction.followup.send("you don't have the later role!")
        jobs = db.get_later_deletion_jobs_by_id(str(user.id))
        for job in jobs:
            try:
                log.info("removing job: " + str(job[2]))
                self.scheduler.remove_job(job[2])
            except Exception as e:
                log.warning(e)
        db.delete_later_jobs_by_id(str(user.id))
        update_later_min_lb(str(user.id))

    @app_commands.command(
        name="unlaterboard",
        description="leaderboard for times /unlater was called",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    async def unlater_leaderboard(self, interaction: Interaction):
        await interaction.response.defer()
        table = db.get_unlater_leaderboard()
        i = 1
        leaderboard = "## /unlater leaderboard\n"
        unknown_users = []
        for row in table:
            try:
                user: User = self.client.get_user(row[0])
                if user is None:
                    user: User = await self.client.fetch_user(row[0])
            except:
                unknown_users.append(row[0])
                continue
            leaderboard += f"\#{i:>3}: **{user.display_name}** - {row[1]} unlaters\n"
            i += 1
        log.info("unknown users: {}".format(unknown_users))
        await interaction.followup.send(leaderboard)

    @app_commands.command(
        name="laterboard",
        description="leaderboard for the total time spent in /later",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    async def later_min_lb(self, interaction: Interaction):
        await interaction.response.defer()
        table = db.get_later_min_leaderboard()
        i = 1
        leaderboard = "## time user spent in /later leaderboard\n"
        unknown_users = []
        for row in table:
            try:
                user: User = self.client.get_user(row[0])
                if user is None:
                    user: User = await self.client.fetch_user(row[0])
            except:
                unknown_users.append(row[0])
                continue
            leaderboard += f"\#{i:>3}: **{user.display_name}** - {row[1]} minutes\n"
            i += 1
        log.info("unknown users: {}".format(unknown_users))
        await interaction.followup.send(leaderboard)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Later(bot))
