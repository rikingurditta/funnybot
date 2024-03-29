import logging
import sys
import traceback
from enum import Enum
from typing import Literal

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.dates import date2num, num2date, ticker

sys.path.append("..")
import discord
import emojis
from discord import Interaction, User, app_commands
from discord.ext import commands
from oi_discord_bot.oi_utils import (
    get_user,
    emoji_str_to_emoji,
    datetime_str_convert_vectorized,
)
from oi_discord_bot.config import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(" "message)s",
    handlers=[logging.FileHandler("oi.log"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def get_emoji_enum():
    emoji_dict = db.get_cumcry_id_emoji_pairs()
    emojis_only = [emoji_str_to_emoji(v) for k, v in emoji_dict.items()]
    emoji_dict = {emoji_str_to_emoji(v): k for k, v in emoji_dict.items()}
    return Literal[tuple(emojis_only)], emoji_dict


Literal_Emojis, emoji_id_map = get_emoji_enum()


class CumCry(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(
        name="hileaderboard",
        description="leaderboard for messages in #hi chat",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    async def hi_leaderboard(self, interaction: Interaction):
        await interaction.response.defer()
        table = db.get_hi_leaderboard()
        i = 1
        leaderboard = "## hi chat leaderboard\n"
        unknown_users = []
        for row in table:
            try:
                user: User = self.client.get_user(row[0])
                if user is None:
                    user: User = await self.client.fetch_user(row[0])
            except:
                unknown_users.append(row[0])
                continue
            leaderboard += f"\#{i:>3}: **{user.display_name}** - {row[1]} messages\n"
            i += 1
        log.info("unknown users: " + str(unknown_users))
        await interaction.followup.send(leaderboard)

    @app_commands.command(
        name="hangmanleaderboard",
        description="leaderboard for sigma hangman wins",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    async def hangman_leaderboard(self, interaction: Interaction):
        await interaction.response.defer()
        table = db.get_hangman_lb()
        i = 1
        leaderboard = "## hangman winners leaderboard\n"
        leaderboard += "```\n"
        leaderboard += f'| {"rank":>4} | {"wins":>4} | {"ratio":>5} | {"name":^20} |\n'
        unknown_users = []
        for row in table:
            if row[1] == 0:
                # skip players with 0 wins
                continue
            try:
                user: User = self.client.get_user(row[0])
                if user is None:
                    user: User = await self.client.fetch_user(row[0])
            except:
                unknown_users.append(row[0])
                continue
            leaderboard += f'| {i:>4} | {row[1]:>4} | {round(row[1]/max(row[2] + row[1], 1), 2):>5} | {user.display_name[:20]:<20} |\n'
            i += 1
        leaderboard += "```"
        log.info("unknown users: " + str(unknown_users))
        await interaction.followup.send(leaderboard)

    async def cumcry_leaderboard(self, interaction: Interaction, action):
        await interaction.response.defer()
        table = None
        if action == "cum":
            table = db.get_cum_leaderboard()
        elif action == "cry":
            table = db.get_cry_leaderboard()
        else:
            return
        i = 1
        leaderboard = f"## {action} leaderboard\n"
        unknown_users = []
        for row in table:
            try:
                user: User = self.client.get_user(row[0])
                if user is None:
                    user: User = await self.client.fetch_user(row[0])
            except:
                unknown_users.append(row[0])
                continue
            cumtext = f"cum: {row[2]:>3}"
            crytext = f"cry: {row[3]:>3}"
            leaderboard += f"\#{i:>3}: {emojis.encode(f':{row[1]}:')} - "
            if action == "cum":
                leaderboard += f"{cumtext}\n"
            else:
                leaderboard += f"{crytext}\n"
            i += 1
        log.info("unknown users: " + str(unknown_users))
        await interaction.followup.send(leaderboard)

    @app_commands.command(
        name="cumleaderboard",
        description="cum leaderboard",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    async def cum_leaderboard(self, interaction: Interaction):
        await self.cumcry_leaderboard(interaction, "cum")

    @app_commands.command(
        name="cryleaderboard",
        description="cry leaderboard",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    async def cry_leaderboard(self, interaction: Interaction):
        await self.cumcry_leaderboard(interaction, "cry")

    @app_commands.command(
        name="cumsandcrys",
        description="cums and cries aggregated leaderboard",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    async def cumsandcrys_leaderboard(self, interaction: Interaction):
        await interaction.response.defer()
        table = db.get_aggregated_cumcry_leaderboard()
        i = 1
        leaderboard = f"## cums and crys leaderboard\n"
        unknown_users = []
        for row in table:
            try:
                user: User = self.client.get_user(row[0])
                if user is None:
                    user: User = await self.client.fetch_user(row[0])
            except:
                unknown_users.append(row[0])
                continue
            leaderboard += f"\#{i:>3}: {emojis.encode(f':{row[1]}:')} - cums and cries: {row[2]:>3}\n"
            i += 1
        log.info("unknown users: " + str(unknown_users))
        await interaction.followup.send(leaderboard)

    @app_commands.command(
        name="clearcumcry",
        description="Requires OI bot dev role - clear cum/cry records",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def clear_cumcry(self, interaction: Interaction):
        await interaction.response.defer()
        # clear_cumcry_counts()
        # await interaction.followup.send(content='cums and cries cleared')
        await interaction.followup.send(content="function disabled")

    @app_commands.command(
        name="forcecumcry",
        description="DO NOT RUN THIS MORE THAN ONCE - gathers cumcry records",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def forcecumcry(self, interaction: Interaction):
        await interaction.response.defer()
        # ret_string = "Gathered counts: \n"
        # entries = db.get_all_cumcry_entries()
        # for entry in entries:
        #     try:
        #         user: discord.User = await get_user(
        #             self.client, entry[0]
        #         )
        #         dm_channel = user.dm_channel
        #         if dm_channel is None:
        #             logging.warning(f"DM channel not found for {user.display_name}")
        #             dm_channel = await user.create_dm()
        #             await asyncio.sleep(10)
        #         async for message in dm_channel.history(limit=1000):
        #             if message.author.id == self.client.user.id:
        #                 continue
        #             l = message.content.lower().strip().split()
        #             if len(l) == 0:
        #                 continue
        #             m = l[0]
        #             if m == "cum":
        #                 db.insert_cum_date_entry(entry[0], message.created_at)
        #             elif m == "cry":
        #                 db.insert_cry_date_entry(entry[0], message.created_at)
        #         total_cry_count = db.count_cry_date_entries_by_id(entry[0])
        #         total_cum_count = db.count_cum_date_entries_by_id(entry[0])
        #         print(total_cum_count, total_cry_count)
        #         ret_string += (
        #             f"{entry[1]}: cum: {total_cum_count} cry: {total_cry_count}\n"
        #         )
        #     except Exception as e:
        #         print(entry[0])
        #         print(e)
        #         traceback.print_exc()
        #         continue
        # await interaction.followup.send(content=ret_string)
        await interaction.followup.send(content="function disabled")

    @app_commands.command(
        name="cdf",
        description="cum/cry distribution function",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.describe(
        mode="which dataset to plot (default is cum)",
        member="which person to target",
    )
    async def cdf(
        self,
        interaction: Interaction,
        mode: Literal["cum", "cry"],
        member: Literal_Emojis,
    ):
        await interaction.response.defer()
        if mode == "cum":
            data = db.get_cum_date_entries_by_id(emoji_id_map[member])
        else:
            data = db.get_cry_date_entries_by_id(emoji_id_map[member])
        data = [d[0] for d in data]
        datetime_arr = datetime_str_convert_vectorized(data)
        log.info("done datetime conversion")
        num_dates = [date2num(d) for d in datetime_arr]
        histo = np.histogram(num_dates)
        cumulative_histo_counts = histo[0].cumsum()
        histo = np.append(histo[1], date2num(datetime.datetime.now()))
        cumulative_histo_counts = np.append(
            cumulative_histo_counts, cumulative_histo_counts[-1]
        )
        plt.plot(histo[1:], cumulative_histo_counts)
        plt.gca().xaxis.set_major_formatter(
            ticker.FuncFormatter(
                lambda numdate, _: num2date(numdate).strftime("%m-%d-%Y")
            )
        )
        plt.gcf().autofmt_xdate()
        plt.savefig("cdf.png")
        plt.clf()
        await interaction.followup.send(file=discord.File("cdf.png"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CumCry(bot))
