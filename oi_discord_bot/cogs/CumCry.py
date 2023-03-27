import sys
sys.path.append("..")
import discord
import emojis
from discord import Interaction, User, app_commands
from discord.ext import commands
from oi_discord_bot.config import *
from oi_discord_bot.onlyimages import tree


class DailyPlots(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @tree.command(
        name="hileaderboard",
        description="leaderboard for messages in #hi chat",
        guild=discord.Object(id=OI_GUILD_ID),
    )
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

    @tree.command(
        name="cumleaderboard",
        description="cum leaderboard",
        guild=discord.Object(id=OI_GUILD_ID),
    )
    async def cum_leaderboard(self, interaction: Interaction):
        await self.cumcry_leaderboard(interaction, "cum")

    @tree.command(
        name="cryleaderboard",
        description="cry leaderboard",
        guild=discord.Object(id=OI_GUILD_ID),
    )
    async def cry_leaderboard(self, interaction: Interaction):
        await self.cumcry_leaderboard(interaction, "cry")

    @tree.command(
        name="cumsandcrys",
        description="cums and cries aggregated leaderboard",
        guild=discord.Object(id=OI_GUILD_ID),
    )
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

    @tree.command(
        name="clearcumcry",
        description="clear cum/cry records",
        guild=discord.Object(id=OI_GUILD_ID),
    )
    @app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
    async def clear_cumcry(self, interaction: Interaction):
        # clear_cumcry_counts()
        # await interaction.followup.send(content='cums and cries cleared')
        await interaction.followup.send(content="function disabled")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DailyPlots(bot))
