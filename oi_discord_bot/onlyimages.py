import asyncio
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


tz = pytz.timezone("Canada/Eastern")

try:
    os.environ["DISCORD_TOKEN"]
except KeyError:
    print("no discord token idiot")
    sys.exit(1)

intents = discord.Intents(
    messages=True, reactions=True, guilds=True, message_content=True, members=True
)
client = commands.Bot(command_prefix=CMD_PREFIX, intents=intents)
tree = client.tree


async def load_extensions():
    for cog_file in ["DailyPlots.DailyPlots", "Confessions", "CumCry", "WYR", "Later"]:
        try:
            await client.load_extension(f"cogs.{cog_file}")
            print(f"Loaded extension {cog_file}")
        except (
            commands.ExtensionNotFound,
            commands.ExtensionAlreadyLoaded,
            commands.NoEntryPointError,
            commands.ExtensionFailed,
        ) as e:
            traceback.print_exc()
            print(f"Could not load extension - {e}")


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    purge_hi_chat_loop.start()
    await tree.sync(guild=discord.Object(id=OI_GUILD_ID))


@client.event
async def on_message(message):
    if "cum" in message.content.lower():
        await message.add_reaction("<:lfg:961074481219117126>")

    if message.channel.id == HI_CHAT_ID:
        db.update_message_count(message.author.id)
        print(f"deleting {message.id} in 15 minutes")
        await message.delete(delay=900)

    if message.author == client.user:
        return

    if not message.guild:
        await process_dm(message)

    if (
        message.guild
        and (message.content != "" or len(message.attachments) == 0)
        and message.channel.name == IMAGES_CHANNEL_NAME
    ):
        print(f"deleting non only image in #{IMAGES_CHANNEL_NAME}")
        print(message.channel.name)
        await message.delete()

    if "\U0001F577" in message.content.lower():
        await message.reply("\U0001F578 SOME HUMAN", mention_author=True)


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


async def process_dm(message):
    l = message.content.lower().strip().split()
    if len(l) == 0:
        return
    m = l[0]
    if m == "cum":
        await message.add_reaction(random.choice(CUM_EMOJIS))
        db.increment_cumcry_count(message.author.id, "cum")
    elif m == "cry":
        await message.add_reaction(random.choice(CRY_EMOJIS))
        db.increment_cumcry_count(message.author.id, "cry")
    elif m == "confess":
        h = db.store_confession(message.content)
        await message.add_reaction(random.choice(CONFESS_EMOJIS))
        await message.reply(h, mention_author=True)
    elif m == "unconfess":
        if len(l) > 1:
            num_rows = db.delete_confession_by_hash(l[1])
            if num_rows > 0:
                await message.add_reaction("🗑️")
            else:
                await message.reply("Invalid hash!", mention_author=True)
    elif m == "wyr":
        h = db.store_wyr(message.content)
        await message.add_reaction(random.choice(WYR_REACT_EMOJIS))
        await message.reply(h, mention_author=True)
    elif m == "unwyr":
        if len(l) > 1:
            await message.add_reaction("🗑️")
            db.delete_wyr_by_hash(l[1])
    else:
        await message.reply(
            "start your message with either `cum`, `cry`, `wyr`, `confess`, `unwyr`, or `unconfess`",
            mention_author=True,
        )


async def main():
    await load_extensions()
    async with client:
        await client.start(os.environ["DISCORD_TOKEN"])


asyncio.run(main())
