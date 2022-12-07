import discord
import os
import sys
import datetime
from discord.ext import tasks
from discord import TextChannel

STAR_THRESHOLD = 5
DEL_THRESHOLD = 5
IMAGES_CHANNEL_NAME = 'images'
HI_CHAT_ID = 1032482927394693178

try:
    os.environ['DISCORD_TOKEN']
except KeyError:
    print('no discord token idiot')
    sys.exit(1)

intents = discord.Intents(messages=True, reactions=True, guilds=True, message_content=True)
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    purge_hi_chat_loop.start()


@client.event
async def on_message(message):
    if message.channel.id == HI_CHAT_ID:
        print(f'deleting {message.content} in 15 minutes')
        await message.delete(delay=900)

    if message.author == client.user:
        return

    if (message.content != '' or len(message.attachments) == 0) and message.channel.name == IMAGES_CHANNEL_NAME:
        print(f'deleting non only image in #{IMAGES_CHANNEL_NAME}')
        print(message.channel.name)
        await message.delete()


async def get_message_by_id(guild_id, channel_id, message_id):
    channel = client.get_guild(guild_id).get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    return message


@client.event
async def on_raw_reaction_add(raw_reaction_event):
    message = await get_message_by_id(raw_reaction_event.guild_id, raw_reaction_event.channel_id,
                                      raw_reaction_event.message_id)
    reactions = message.reactions

    print("reaction {}".format(raw_reaction_event.emoji.name))

    if raw_reaction_event.emoji.name == '⭐':
        for react in reactions:
            if react.emoji == '⭐' and react.count >= STAR_THRESHOLD:
                print(f'starring {STAR_THRESHOLD}x⭐')
                await message.pin()

    elif raw_reaction_event.emoji.name == '👎' and message.channel.name == IMAGES_CHANNEL_NAME:
        for react in reactions:
            if react.emoji == '👎' and react.count >= DEL_THRESHOLD:
                print(f'deleting {DEL_THRESHOLD}x👎')
                await message.delete()
                break


async def purge_hi_chat():
    print('purging hi chat')
    channel: TextChannel = client.get_channel(HI_CHAT_ID)

    try:
        async for msg in channel.history(limit=500):
            if msg.created_at < datetime.datetime.now() - datetime.timedelta(minutes=15):
                print(f'deleting {msg.content} through 15 min loop')
                await msg.delete()
    except:
        pass


@tasks.loop(minutes=15)
async def purge_hi_chat_loop():
    await purge_hi_chat()

client.run(os.environ['DISCORD_TOKEN'])
