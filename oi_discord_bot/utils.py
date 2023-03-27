from config import *


async def remove_role(user, role):
    await user.remove_roles(role, "scheduled role removal by oi_discord_bot")


async def get_role(client, role_id):
    guild = client.get_guild(OI_GUILD_ID)
    if guild is None:
        guild = await client.fetch_guild(OI_GUILD_ID)
    return guild.get_role(role_id)


async def get_message_by_id(client, guild_id, channel_id, message_id):
    guild = await client.fetch_guild(guild_id)
    # print(guild)
    channel = await guild.fetch_channel(channel_id)
    # print(channel)
    message = await channel.fetch_message(message_id)
    return message
