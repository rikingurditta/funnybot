import asyncio
from time import sleep
import datetime
from datetime import timezone
import hashlib

import discord
import os
import sys
import random
from discord.ext import tasks, commands
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
import emojis

from oi_daily_plot_functions import make_daily_graph
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

STAR_THRESHOLD = 5
DEL_THRESHOLD = 5
IMAGES_CHANNEL_NAME = "images"

OI_GUILD_ID = 961028480189992970
GENERAL_CHANNEL_ID = 1032482385205415947
HI_CHAT_ID = 1032482927394693178
BESTOF_CHANNEL_ID = 1075618133571809281
OI_DEV_ROLE_ID = 1081679547302420541
RIIN_ROLE_ID = 1035448479742427196
BOT_TEST_STUFF_CHANNEL_ID = 961029138129490032
CONFESSIONS_CHANNEL_ID = GENERAL_CHANNEL_ID
WYR_CHANNEL_ID = GENERAL_CHANNEL_ID


CUM_EMOJIS = ["💦", "🥵", "🤢", "🥛", "😋"]
CRY_EMOJIS = ["😢", "🫂", "😭", "😔", "☹️"]
CONFESS_EMOJIS = ["😳", "‼️", "⁉️", "💀", "😱"]
WYR_EMOJIS = ["🅰️", "🅱️"]
WYR_REACT_EMOJIS = ["🤔", "💭"]


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
if db_version < 2:
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS cumcry (id TEXT NOT NULL, emoji TEXT NOT NULL, cumcount INT NOT NULL, crycount INT NOT NULL)"
    )
    cursor.execute("CREATE TABLE IF NOT EXISTS confessions (confession TEXT NOT NULL)")
if db_version < 3:
    cursor.execute("CREATE TABLE IF NOT EXISTS wyr (question TEXT NOT NULL)")
if db_version < 4:
    cursor.execute("ALTER TABLE confessions ADD COLUMN IF NOT EXISTS hash TEXT")
    cursor.execute("ALTER TABLE wyr ADD COLUMN IF NOT EXISTS hash TEXT")
LATEST_VERSION = 4
if db_version == 0:
    cursor.execute("INSERT INTO schema_version VALUES ?", (LATEST_VERSION,))
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


def get_cum_leaderboard():
    cursor.execute(
        "SELECT id, emoji, cumcount, crycount FROM cumcry ORDER BY cumcount DESC"
    )
    return cursor.fetchall()


def get_cry_leaderboard():
    cursor.execute(
        "SELECT id, emoji, cumcount, crycount FROM cumcry ORDER BY crycount DESC"
    )
    return cursor.fetchall()


def get_aggregated_cumcry_leaderboard():
    cursor.execute(
        "SELECT id, emoji, cumcount + crycount FROM cumcry ORDER BY cumcount + crycount DESC, cumcount DESC"
    )
    return cursor.fetchall()


def increment_cumcry_count(id, action):
    cursor.execute("SELECT * FROM cumcry WHERE id = ?", (id,))
    if len(cursor.fetchall()) == 0:
        # choose random emoji from 'Animals & Nature' category
        cat = [*emojis.db.get_emojis_by_category("Animals & Nature")]
        e = random.choice(cat)
        # check if anyone else has same emoji
        cursor.execute("SELECT * FROM cumcry WHERE emoji = ?", (e.aliases[0],))
        # repeat until we find one that no one else has
        while len(cursor.fetchall()) > 0:
            e = random.choice(cat)
            cursor.execute("SELECT * FROM cumcry WHERE emoji = ?", (e.aliases[0],))
        # create entry for user with their unique emoji
        cursor.execute("INSERT INTO cumcry VALUES (?, ?, 0, 0)", (id, e.aliases[0]))
    # update counts
    if action == "cum":
        cursor.execute("UPDATE cumcry SET cumcount = cumcount + 1 WHERE id = ?", (id,))
    elif action == "cry":
        cursor.execute("UPDATE cumcry SET crycount = crycount + 1 WHERE id = ?", (id,))
    connection.commit()


def clear_cumcry_counts():
    cursor.execute("DELETE FROM cumcry")
    connection.commit()


def store_confession(confession):
    confession = confession[len('confess '):]
    h = hashlib.sha1(confession.encode('utf-8')).hexdigest()
    cursor.execute("INSERT INTO confessions VALUES (?, ?)", (confession, h))
    connection.commit()
    return h


def store_wyr(wyr):
    wyr = wyr[len('wyr '):]
    h = hashlib.sha1(wyr.encode('utf-8')).hexdigest()
    cursor.execute("INSERT INTO wyr VALUES (?, ?)", (wyr, h))
    connection.commit()
    return h


def get_random_confession():
    cursor.execute("SELECT rowid, * FROM confessions ORDER BY RANDOM() LIMIT 1")
    table = cursor.fetchall()
    rowid = -1
    confession = ""
    if len(table) > 0:
        rowid = table[0][0]
        confession = table[0][1]
    return rowid, confession


def get_random_wyr():
    cursor.execute("SELECT rowid, * FROM wyr ORDER BY RANDOM() LIMIT 1")
    table = cursor.fetchall()
    rowid = -1
    wyr = ""
    if len(table) > 0:
        rowid = table[0][0]
        wyr = table[0][1]
    return rowid, wyr


def delete_confession(rowid):
    cursor.execute("DELETE FROM confessions WHERE rowid = ?", (rowid,))
    connection.commit()


def delete_confession_by_hash(h):
    cursor.execute("DELETE FROM confessions WHERE hash = ?", (h,))
    connection.commit()


def delete_wyr(rowid):
    cursor.execute("DELETE FROM wyr WHERE rowid = ?", (rowid,))
    connection.commit()


def delete_wyr_by_hash(h):
    cursor.execute("DELETE FROM wyr WHERE hash = ?", (h,))
    connection.commit()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    await tree.sync(guild=discord.Object(id=OI_GUILD_ID))
    purge_hi_chat_loop.start()

    # rose plot scheduler
    scheduler = AsyncIOScheduler()
    #scheduler.add_job(post_plot_job, CronTrigger(hour="12", minute="0", second="0"))
    scheduler.add_job(post_confession, CronTrigger(hour="18", minute="0", second="0"))
    scheduler.add_job(post_wyr, CronTrigger(hour="12", minute="0", second="0"))
    scheduler.start()


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

    if not message.guild:
        await process_dm(message)

    if message.guild and (
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


@tree.command(
    name="forceplot",
    description="Force rose's daily plot to be posted",
    guild=discord.Object(id=OI_GUILD_ID),
)
@app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
async def force_run_daily_plot(interaction: Interaction):
    await interaction.response.defer()
    make_daily_graph("oi_responses.csv", "oi_biases.tsv")
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
        leaderboard += f"#{i:>3}: **{user.display_name}** - {row[1]} messages\n"
        i += 1
    print(unknown_users)
    await interaction.followup.send(leaderboard)


async def post_plot_job():
    make_daily_graph("oi_responses.csv", "oi_biases.tsv")
    channel: TextChannel = client.get_channel(GENERAL_CHANNEL_ID)
    if channel is None:
        channel: TextChannel = await client.fetch_channel(GENERAL_CHANNEL_ID)
    await channel.send(file=discord.File("dailygraph.png"))


async def cumcry_leaderboard(interaction: Interaction, action):
    await interaction.response.defer()
    table = None
    if action == "cum":
        table = get_cum_leaderboard()
    elif action == "cry":
        table = get_cry_leaderboard()
    else:
        return
    i = 1
    leaderboard = f"{action} leaderboard\n"
    unknown_users = []
    for row in table:
        try:
            user: User = client.get_user(row[0])
            if user is None:
                user: User = await client.fetch_user(row[0])
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
async def cum_leaderboard(interaction: Interaction):
    await cumcry_leaderboard(interaction, "cum")


@tree.command(
    name="cryleaderboard",
    description="cry leaderboard",
    guild=discord.Object(id=OI_GUILD_ID),
)
async def cry_leaderboard(interaction: Interaction):
    await cumcry_leaderboard(interaction, "cry")


@tree.command(
    name="cumsandcrys",
    description="cums and cries aggregated leaderboard",
    guild=discord.Object(id=OI_GUILD_ID),
)
async def cumsandcrys_leaderboard(interaction: Interaction):
    await interaction.response.defer()
    table = get_aggregated_cumcry_leaderboard()
    i = 1
    leaderboard = f"cums and crys leaderboard\n"
    unknown_users = []
    for row in table:
        try:
            user: User = client.get_user(row[0])
            if user is None:
                user: User = await client.fetch_user(row[0])
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
async def clear_cumcry(interaction: Interaction):
    # clear_cumcry_counts()
    # await interaction.followup.send(content='cums and cries cleared')
    await interaction.followup.send(content='function disabled')


@tree.command(
    name="forceconfess",
    description="Force confession to be posted",
    guild=discord.Object(id=OI_GUILD_ID),
)
@app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
async def force_confess(interaction: Interaction):
    await interaction.response.defer()
    rowid, confession = get_random_confession()
    if confession == '':
        await interaction.followup.send(content='no confessions')
    else:
        delete_confession(rowid)
        await interaction.followup.send(content='confession', embed=Embed(description=confession))


@tree.command(
    name="forcewyr",
    description="Force WYR to be posted",
    guild=discord.Object(id=OI_GUILD_ID),
)
@app_commands.checks.has_any_role(OI_DEV_ROLE_ID)
async def force_wyr(interaction: Interaction):
    await interaction.response.defer()
    rowid, wyr = get_random_wyr()
    if wyr == '':
        await interaction.followup.send(content='no options')
    else:
        delete_wyr(rowid)
        message = await interaction.followup.send(content='Would you rather', embed=Embed(description=wyr))
        for emoji in WYR_EMOJIS:
            await message.add_reaction(emoji)


async def post_confession():
    rowid, confession = get_random_confession()
    if confession == '':
        return
    delete_confession(rowid)
    if confession != "":
        channel: TextChannel = await client.fetch_channel(CONFESSIONS_CHANNEL_ID)
        await channel.send(content='confession', embed=Embed(description=confession))


async def post_wyr():
    rowid, wyr = get_random_wyr()
    if wyr == '':
        return
    delete_wyr(rowid)
    if wyr != "":
        channel: TextChannel = await client.fetch_channel(WYR_CHANNEL_ID)
        message = await channel.send(content='Would you rather', embed=Embed(description=wyr))
        for emoji in WYR_EMOJIS:
            await message.add_reaction(emoji)


async def process_dm(message):
    l = message.content.lower().strip().split()
    if len(l) == 0:
        return
    m = l[0]
    if m == "cum":
        await message.add_reaction(random.choice(CUM_EMOJIS))
        increment_cumcry_count(message.author.id, "cum")
    elif m == "cry":
        await message.add_reaction(random.choice(CRY_EMOJIS))
        increment_cumcry_count(message.author.id, "cry")
    elif m == "confess":
        h = store_confession(message.content)
        await message.add_reaction(random.choice(CONFESS_EMOJIS))
        await message.reply(h, mention_author=True)
    elif m == 'unconfess':
        if len(l) > 1:
            await message.add_reaction('🗑️')
            delete_confession_by_hash(l[1])
    elif m == "wyr":
        h = store_wyr(message.content)
        await message.add_reaction(random.choice(WYR_REACT_EMOJIS))
        await message.reply(h, mention_author=True)
    elif m == 'unwyr':
        if len(l) > 1:
            await message.add_reaction('🗑️')
            delete_wyr_by_hash(l[1])
    else:
        await message.reply(
            "start your message with either `cum`, `cry`, `wyr`, `confess`, `unwyr`, or `unconfess`",
            mention_author=True,
        )


client.run(os.environ["DISCORD_TOKEN"])
