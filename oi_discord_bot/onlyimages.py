import re
import traceback
from time import sleep
import datetime

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
)
import pytz

from config import *
from utils import get_channel, backup_oi_db, backup_oi_log
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(" "message)s",
    handlers=[logging.FileHandler("oi.log"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


tz = pytz.timezone("Canada/Eastern")

try:
    os.environ["DISCORD_TOKEN"]
except KeyError:
    log.critical("no discord token idiot")
    sys.exit(1)

intents = discord.Intents(
    messages=True, reactions=True, guilds=True, message_content=True, members=True
)
client = commands.Bot(command_prefix=CMD_PREFIX, intents=intents)


async def load_extensions():
    for cog_file in [
        "Confessions",
        "CumCry",
        "WYR",
        "Later",
        "DailyPlots.DailyPlots",
        "Utils",
    ]:
        try:
            await client.load_extension(f"cogs.{cog_file}")
            log.info(f"Loaded extension {cog_file}")
        except (
            commands.ExtensionNotFound,
            commands.ExtensionAlreadyLoaded,
            commands.NoEntryPointError,
            commands.ExtensionFailed,
        ) as e:
            traceback.print_exc()
            log.error(f"Could not load extension - {e}")


@client.event
async def on_ready():
    log.info("We have logged in as {0.user}".format(client))
    purge_hi_chat_loop.start()
    backup_oi_db_loop.start()
    purge_one_min_loop.start()


loss_regex = re.compile(r"Ooh, sorry (.*), it was [a-z]+?\.")
win_regex = re.compile(r"Correct, (.*), it was [a-z]+?\.")


@client.event
async def on_message(message):
    if message.author.id == SIGMA_BOT_ID:
        if len(message.embeds) > 0:
            embed_dict = message.embeds[0].to_dict()
            if "title" in embed_dict:
                loss_results = loss_regex.findall(embed_dict["title"])
                win_results = win_regex.findall(embed_dict["title"])
                hangman_member = None
                win = False
                if len(loss_results) > 0:
                    hangman_member = message.guild.fetch_member(loss_results[0])
                    if hangman_member is None:
                        log.error(
                            "could not find hangman member {}".format(
                                message.author.name
                            )
                        )
                elif len(win_results) > 0:
                    hangman_member = message.guild.fetch_member(win_results[0])
                    if hangman_member is None:
                        log.error(
                            "could not find hangman member {}".format(
                                message.author.name
                            )
                        )
                    win = True
                if hangman_member is not None:
                    if len(loss_results) > 0 or len(win_results) > 0:
                        db.increment_hangman_lb(hangman_member.id, win)

    if "cum" in message.content.lower():
        await message.add_reaction("<:lfg:961074481219117126>")

    if message.channel.id == HI_CHAT_ID:
        db.update_message_count(message.author.id)
        log.info(f"deleting {message.id} in 15 minutes")
        await message.delete(delay=900)

    if message.channel.id == ONE_MIN_CHANNEL_ID:
        log.info(f"deleting {message.id} in 1 minute")
        await message.delete(delay=60)

    if message.author == client.user:
        return

    if not message.guild:
        await process_dm(message)

    if (
        message.guild
        and (message.content != "" or len(message.attachments) == 0)
        and message.channel.name == IMAGES_CHANNEL_NAME
    ):
        log.info(f"deleting non only image in #{IMAGES_CHANNEL_NAME}")
        log.info(message.channel.name)
        await message.delete()

    if "\U0001F577" in message.content.lower():
        await message.reply("\U0001F578 SOME HUMAN", mention_author=True)


@client.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    if payload.emoji.name == "⭐" and payload.channel_id != BESTOF_CHANNEL_ID:
        # we do this to limit the amount of API calls we make
        channel: TextChannel = await get_channel(client, payload.channel_id)
        message: Message = await channel.fetch_message(payload.message_id)
        reactions = message.reactions
        log.info("reaction {}".format(payload.emoji.name))
        for react in reactions:
            if react.emoji == "⭐" and react.count >= STAR_THRESHOLD:
                if payload.channel_id == HI_CHAT_ID:
                    await message.pin()
                    return
                log.info(f"starring {STAR_THRESHOLD}x⭐")
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

    elif payload.emoji.name == "👎" and payload.channel_id == IMAGES_CHANNEL_ID:
        # we do this to limit the amount of API calls we make
        channel: TextChannel = await get_channel(client, payload.channel_id)
        message: Message = await channel.fetch_message(payload.message_id)
        reactions = message.reactions
        log.info("reaction {}".format(payload.emoji.name))
        for react in reactions:
            if react.emoji == "👎" and react.count >= DEL_THRESHOLD:
                log.info(f"deleting {DEL_THRESHOLD}x👎")
                await message.delete()
                break


async def purge_hi_chat():
    log.info("purging hi chat")
    channel: TextChannel = client.get_channel(HI_CHAT_ID)
    if channel is None:
        channel: TextChannel = await client.fetch_channel(HI_CHAT_ID)
    messages = [m async for m in channel.history(limit=100)]

    for msg in messages:
        log.info(
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
            log.info(f"deleting {msg.id} through 15 min loop")
            await msg.delete()
            sleep(2)


@tasks.loop(minutes=15)
async def purge_hi_chat_loop():
    await purge_hi_chat()


@tasks.loop(minutes=5)
async def purge_one_min_loop():
    await purge_one_min()


async def purge_one_min():
    log.info("purging #1-min chat")
    channel: TextChannel = client.get_channel(ONE_MIN_CHANNEL_ID)
    if channel is None:
        channel: TextChannel = await client.fetch_channel(ONE_MIN_CHANNEL_ID)
    messages = [m async for m in channel.history(limit=100)]

    for msg in messages:
        log.info(
            "msg created at: {}, now: {}, now - 1min: {}".format(
                msg.created_at.astimezone(pytz.utc),
                tz.normalize(datetime.datetime.now(tz)).astimezone(pytz.utc),
                tz.normalize(datetime.datetime.now(tz)).astimezone(pytz.utc)
                - datetime.timedelta(minutes=1),
            )
        )
        if msg.created_at.astimezone(pytz.utc) < tz.normalize(
            datetime.datetime.now(tz)
        ).astimezone(pytz.utc) - datetime.timedelta(minutes=1):
            log.info(f"deleting {msg.id} in #1-min through 5 min loop")
            await msg.delete()
            sleep(2)


@tasks.loop(hours=24)
async def backup_oi_db_loop():
    backup_oi_db()


@tasks.loop(hours=48)
async def backup_oi_log_loop():
    backup_oi_log()


async def process_dm(message):
    l = message.content.lower().strip().split()
    if len(l) == 0:
        return
    m = l[0]
    if m == "sync" and message.author.id in OI_BOT_DEV_IDS:
        await client.tree.sync(guild=discord.Object(id=OI_GUILD_ID))
        await message.reply("syncing complete")
        return
    if m == "cum":
        await message.add_reaction(random.choice(CUM_EMOJIS))
        db.increment_cumcry_count(message.author.id, "cum")
        db.insert_cum_date_entry(message.author.id, message.created_at)
    elif m == "cry":
        await message.add_reaction(random.choice(CRY_EMOJIS))
        db.increment_cumcry_count(message.author.id, "cry")
        db.insert_cry_date_entry(message.author.id, message.created_at)
    elif m == "confess":
        if ENABLE_CONFESSIONS:
            h = db.store_confession(message.content)
            await message.add_reaction(random.choice(CONFESS_EMOJIS))
            await message.reply(h, mention_author=True)
        else:
            await message.reply(
                "it's over. no more confessions <:cryer:997566397364314253>",
                mention_author=True,
            )
    elif m == "unconfess":
        if ENABLE_CONFESSIONS:
            if len(l) > 1:
                num_rows = db.delete_confession_by_hash(l[1])
                if num_rows > 0:
                    await message.add_reaction("🗑️")
                else:
                    await message.reply("Invalid hash!", mention_author=True)
        else:
            await message.reply(
                "it's over. no more confessions <:cryer:997566397364314253>",
                mention_author=True,
            )
    elif m == "wyr":
        h = db.store_wyr(message.content)
        await message.add_reaction(random.choice(WYR_REACT_EMOJIS))
        await message.reply(h, mention_author=True)
    elif m == "unwyr":
        if len(l) > 1:
            num_rows = db.delete_wyr_by_hash(l[1])
            if num_rows > 0:
                await message.add_reaction("🗑️")
            else:
                await message.reply("Invalid hash!", mention_author=True)
    else:
        await message.reply(
            "start your message with either `cum`, `cry`, `wyr`, `confess`, `unwyr`, or `unconfess`",
            mention_author=True,
        )


async def main():
    await load_extensions()
    async with client:
        await client.start(os.environ["DISCORD_TOKEN"])
        await client.tree.sync(guild=discord.Object(id=OI_GUILD_ID))


# do this so asyncio.run() doesn't trigger every time oi_discord_bot is imported
if __name__ == "__main__":
    asyncio.run(main())
