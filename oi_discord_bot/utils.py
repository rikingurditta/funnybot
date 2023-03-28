import discord
from config import *
from discord.ext import commands
from datetime import datetime


async def get_role(client: commands.Bot, role_id) -> discord.Role:
    guild = client.get_guild(OI_GUILD_ID)
    if guild is None:
        guild = await client.fetch_guild(OI_GUILD_ID)
    return guild.get_role(role_id)


async def get_user(client: commands.Bot, user_id) -> discord.User:
    user = client.get_user(user_id)
    if user is None:
        user = await client.fetch_user(user_id)
    return user


async def get_channel(client: commands.Bot, channel_id):
    channel = client.get_channel(channel_id)
    if channel is None:
        channel = await client.fetch_channel(channel_id)
    return channel


async def get_guild(client: commands.Bot, guild_id) -> discord.Guild:
    guild = client.get_guild(guild_id)
    if guild is None:
        guild = await client.fetch_guild(guild_id)
    return guild


async def get_member(client: commands.Bot, member_id, guild_id) -> discord.Member:
    guild = await get_guild(client, guild_id)
    member = await guild.get_member(member_id)
    if member is None:
        member = await guild.fetch_member(guild_id)
    return member


async def get_message_by_id(
    client: commands.Bot, guild_id, channel_id, message_id
) -> discord.Message:
    guild = await client.fetch_guild(guild_id)
    # print(guild)
    channel = await guild.fetch_channel(channel_id)
    # print(channel)
    message = await channel.fetch_message(message_id)
    return message


async def remove_role(client: commands.Bot, role_id, member_id):
    role = await get_role(client, role_id)
    user = await get_member(client, member_id, OI_GUILD_ID)
    await user.remove_roles(role, reason="later timer expired")


def datetime_tz_str_to_datetime(datetime_str):
    format_string = "%Y-%m-%d %H:%M:%S.%f%z"
    return datetime.strptime(datetime_str, format_string)
