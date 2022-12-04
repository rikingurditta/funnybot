import discord
import os
import sys

STAR_THRESHOLD = 5
DEL_THRESHOLD = 5
IMAGES_CHANNEL_NAME = 'images'

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


@client.event
async def on_message(message):
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

    if raw_reaction_event.emoji.name == '⭐':
        for react in reactions:
            if react.emoji == '⭐' and react.count == STAR_THRESHOLD:
                print(f'starring {STAR_THRESHOLD}x⭐')
                await message.pin()

    elif raw_reaction_event.emoji.name == '👎' and message.channel.name == IMAGES_CHANNEL_NAME:
        for react in reactions:
            if react.emoji == '👎' and react.count >= DEL_THRESHOLD:
                print(f'deleting {DEL_THRESHOLD}x👎')
                await message.delete()
                break


client.run(os.environ['DISCORD_TOKEN'])
