import logging
import sys
import traceback

sys.path.append("..")
import discord
import emojis
from discord import Interaction, User, app_commands
from discord.ext import commands
from oi_discord_bot.utils import get_member
from oi_discord_bot.config import *


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
        leaderboard = "#hi chat leaderboard\n"
        unknown_users = []
        for row in table:
            try:
                user: User = self.client.get_user(row[0])
                if user is None:
                    user: User = await self.client.fetch_user(row[0])
            except:
                unknown_users.append(row[0])
                continue
            leaderboard += f"#{i:>3}: **{user.display_name}** - {row[1]} messages\n"
            i += 1
        print(unknown_users)
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
        leaderboard = f"{action} leaderboard\n"
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
            leaderboard += f"#{i:>3}: {emojis.encode(f':{row[1]}:')} - "
            if action == "cum":
                leaderboard += f"{cumtext}\n"
            else:
                leaderboard += f"{crytext}\n"
            i += 1
        print(unknown_users)
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
        leaderboard = f"cums and crys leaderboard\n"
        unknown_users = []
        for row in table:
            try:
                user: User = self.client.get_user(row[0])
                if user is None:
                    user: User = await self.client.fetch_user(row[0])
            except:
                unknown_users.append(row[0])
                continue
            leaderboard += f"#{i:>3}: {emojis.encode(f':{row[1]}:')} - cums and cries: {row[2]:>3}\n"
            i += 1
        print(unknown_users)
        await interaction.followup.send(leaderboard)

    @app_commands.command(
        name="clearcumcry",
        description="clear cum/cry records",
    )
    @app_commands.guilds(discord.Object(id=OI_GUILD_ID))
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def clear_cumcry(self, interaction: Interaction):
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
        ret_string = "Gathered counts: \n"
        entries = db.get_cumcry_entries()
        for entry in entries:
            try:
                member: discord.Member = await get_member(
                    self.client, entry[0], OI_GUILD_ID
                )
                dm_channel = member.dm_channel
                if dm_channel is None:
                    logging.warning(f"DM channel not found for {member.display_name}")
                    continue
                else:
                    async for message in dm_channel.history(limit=1000):
                        if message.author.id == self.client.user.id:
                            continue
                        l = message.content.lower().strip().split()
                        if len(l) == 0:
                            continue
                        m = l[0]
                        if m == "cum":
                            db.insert_cum_date_entry(entry[0], message.created_at)
                        elif m == "cry":
                            db.insert_cry_date_entry(entry[0], message.created_at)
                    total_cry_count = db.get_cry_count(entry[0])
                    total_cum_count = db.get_cum_count(entry[0])
                    ret_string += (
                        f"{entry[1]}: cum: {total_cum_count} cry: {total_cry_count}\n"
                    )
            except Exception as e:
                print(entry[0])
                print(e)
                traceback.print_exc()
                continue
        await interaction.followup.send(content=ret_string)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CumCry(bot))
