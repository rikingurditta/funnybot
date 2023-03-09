import asyncio
from time import sleep
import datetime
from datetime import timezone

import discord
import os
import sys
from discord.ext import tasks
from discord import (
    TextChannel,
    RawReactionActionEvent,
    Embed,
    Message,
    Reaction,
    app_commands,
    Interaction,
    Member,
    User,
)
import pytz
import sqlite3

from oi_daily_plot_functions import make_daily_graph

STAR_THRESHOLD = 5
DEL_THRESHOLD = 5
IMAGES_CHANNEL_NAME = "images"

OI_GUILD_ID = 961028480189992970
GENERAL_CHANNEL_ID = 1032482385205415947
HI_CHAT_ID = 1032482927394693178
BESTOF_CHANNEL_ID = 1075618133571809281
OI_DEV_ROLE_ID = 1081679547302420541

tz = pytz.timezone("Canada/Eastern")

connection = sqlite3.connect("oi.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS schema_version (version INT NOT NULL)")
db_version = cursor.execute("SELECT version FROM schema_version").fetchall()
if len(db_version) == 0:
    db_version = 0
else:
    db_version = db_version[0][0]
if db_version < 1:
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS oi (id TEXT NOT NULL, messagecount INT NOT NULL)"
    )
LATEST_VERSION = 1
if db_version == 0:
    cursor.execute("INSERT INTO schema_version VALUES (1)")
else:
    cursor.execute("UPDATE schema_version SET version = ?", (LATEST_VERSION,))
connection.commit()

try:
    os.environ["DISCORD_TOKEN"]
except KeyError:
    print("no discord token idiot")
    sys.exit(1)

intents = discord.Intents(
    messages=True, reactions=True, guilds=True, message_content=True, members=True
)
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def update_message_count(id):
    cursor.execute("SELECT * FROM oi WHERE id = ?", (id,))
    if len(cursor.fetchall()) == 0:
        cursor.execute("INSERT INTO oi VALUES (?, 1)", (id,))
    else:
        cursor.execute(
            "UPDATE oi SET messagecount = messagecount + 1 WHERE id = ?", (id,)
        )
    connection.commit()


def get_hi_leaderboard():
    cursor.execute("SELECT * FROM oi ORDER BY messagecount DESC")
    return cursor.fetchall()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    await tree.sync(guild=discord.Object(id=OI_GUILD_ID))
    purge_hi_chat_loop.start()


@client.event
async def on_message(message):
    if "cum" in message.content.lower():
        await message.add_reaction("<:lfg:961074481219117126>")

    if message.channel.id == HI_CHAT_ID:
        update_message_count(message.author.id)
        print(f"deleting {message.id} in 15 minutes")
        await message.delete(delay=900)

    if message.author == client.user:
        return

    if (
        message.content != "" or len(message.attachments) == 0
    ) and message.channel.name == IMAGES_CHANNEL_NAME:
        print(f"deleting non only image in #{IMAGES_CHANNEL_NAME}")
        print(message.channel.name)
        await message.delete()

    if "\U0001F577" in message.content.lower():
        await message.reply("\U0001F578 SOME HUMAN", mention_author=True)


async def get_message_by_id(guild_id, channel_id, message_id):
    guild = await client.fetch_guild(guild_id)
    # print(guild)
    channel = await guild.fetch_channel(channel_id)
    # print(channel)
    message = await channel.fetch_message(message_id)
    return message


@client.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    # we do this to limit the amount of API calls we make
    channel: TextChannel = client.get_channel(payload.channel_id)
    if channel is None:
        channel: TextChannel = await client.fetch_channel(payload.channel_id)
    message: Message = await channel.fetch_message(payload.message_id)
    reactions = message.reactions
    print("reaction {}".format(payload.emoji.name))

    if payload.emoji.name == "⭐" and payload.channel_id != BESTOF_CHANNEL_ID:
        for react in reactions:
            if react.emoji == "⭐" and react.count >= STAR_THRESHOLD:
                if payload.channel_id == HI_CHAT_ID:
                    await message.pin()
                    return
                print(f"starring {STAR_THRESHOLD}x⭐")
                bestof_channel: TextChannel = client.get_channel(BESTOF_CHANNEL_ID)
                if bestof_channel is None:
                    bestof_channel: TextChannel = await client.fetch_channel(
                        BESTOF_CHANNEL_ID
                    )
                bestof_msg = f"{message.content}\n\n[Click Here to view context]({message.jump_url})"
                # fetch member instead of user to get the top role color
                author_member = await message.guild.fetch_member(message.author.id)
                embed = Embed(
                    color=author_member.top_role.color,
                    description=bestof_msg,
                    timestamp=message.created_at,
                )

                embed.set_author(
                    name=message.author.display_name, icon_url=message.author.avatar
                )

                footer = f"{message.guild.name} | #{message.channel.name}"
                embed.set_footer(text=footer)
                txt = f"{react.emoji} #** {react.count} **"

                for attachment in message.attachments:
                    if attachment.filename.split(".")[-1].lower() in (
                        "jpg",
                        "jpeg",
                        "png",
                        "webp",
                        "gif",
                        "mp4",
                    ):
                        embed.set_image(url=attachment.url)

                already_posted = False

                # Allow some time between posts to prevent double posting
                await asyncio.sleep(5)
                async for msg in bestof_channel.history(limit=40):
                    for s in msg.embeds:
                        if message.jump_url in s.to_dict()["description"]:
                            prev_post = msg
                            already_posted = True
                if already_posted:
                    await prev_post.edit(content=txt, embed=embed)
                else:
                    await bestof_channel.send(content=txt, embed=embed)

    elif payload.emoji.name == "👎" and message.channel.name == IMAGES_CHANNEL_NAME:
        for react in reactions:
            if react.emoji == "👎" and react.count >= DEL_THRESHOLD:
                print(f"deleting {DEL_THRESHOLD}x👎")
                await message.delete()
                break


async def purge_hi_chat():
    print("purging hi chat")
    channel: TextChannel = client.get_channel(HI_CHAT_ID)
    if channel is None:
        channel: TextChannel = await client.fetch_channel(HI_CHAT_ID)
    messages = [m async for m in channel.history(limit=100)]

    for msg in messages:
        print(
            "msg created at: {}, now: {}, now - 15min: {}".format(
                msg.created_at.astimezone(pytz.utc),
                tz.normalize(datetime.datetime.now(tz)).astimezone(pytz.utc),
                tz.normalize(datetime.datetime.now(tz)).astimezone(pytz.utc)
                - datetime.timedelta(minutes=15),
            )
        )
        if msg.created_at.astimezone(pytz.utc) < tz.normalize(
            datetime.datetime.now(tz)
        ).astimezone(pytz.utc) - datetime.timedelta(minutes=15):
            print(f"deleting {msg.id} through 15 min loop")
            await msg.delete()
            sleep(2)


@tasks.loop(minutes=15)
async def purge_hi_chat_loop():
    await purge_hi_chat()


@tasks.loop(hours=24)
async def post_daily_plot():
    make_daily_graph("oi_responses.tsv", "oi_biases.tsv")
    channel: TextChannel = client.get_channel(GENERAL_CHANNEL_ID)
    if channel is None:
        channel: TextChannel = await client.fetch_channel(GENERAL_CHANNEL_ID)
    await channel.send(file=discord.File("dailygraph.png"))


@tree.command(
    name="forceplot",
    description="Force rose's daily plot to be posted",
    guild=discord.Object(id=OI_GUILD_ID),
)
@app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
async def force_run_daily_plot(interaction: Interaction):
    await interaction.response.defer()
    make_daily_graph("oi_responses.tsv", "oi_biases.tsv")
    await interaction.followup.send(file=discord.File("dailygraph.png"))


@tree.command(
    name="hileaderboard",
    description="leaderboard for messages in #hi chat",
    guild=discord.Object(id=OI_GUILD_ID),
)
async def hi_leaderboard(interaction: Interaction):
    await interaction.response.defer()
    table = get_hi_leaderboard()
    i = 1
    leaderboard = "#hi chat leaderboard\n"
    unknown_users = []
    for row in table:
        try:
            user: User = client.get_user(row[0])
            if user is None:
                user: User = await client.fetch_user(row[0])
        except:
            unknown_users.append(row[0])
            continue
        leaderboard += f"#{i}: **{user.display_name}** - {row[1]} messages\n"
        i += 1
    print(unknown_users)
    await interaction.followup.send(leaderboard)


client.run(os.environ["DISCORD_TOKEN"])
