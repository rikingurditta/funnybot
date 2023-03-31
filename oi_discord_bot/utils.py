import discord
from config import *
from discord.ext import commands
from datetime import datetime
import emojis


async def get_role(client: commands.Bot, role_id) -> discord.Role:
    """
    Gets role from OI guild. Minimizes API calls.
    :param client:
    :param role_id:
    :return:
    """
    guild = client.get_guild(OI_GUILD_ID)
    if guild is None:
        guild = await client.fetch_guild(OI_GUILD_ID)
    return guild.get_role(role_id)


async def get_user(client: commands.Bot, user_id) -> discord.User:
    """
    Get user by calling client. Minimizes API calls.
    :param client:
    :param user_id:
    :return:
    """
    user = client.get_user(user_id)
    if user is None:
        user = await client.fetch_user(user_id)
    return user


async def get_channel(client: commands.Bot, channel_id):
    """
    Get channel by calling client. Minimizes API calls.
    :param client:
    :param channel_id:
    :return:
    """
    channel = client.get_channel(channel_id)
    if channel is None:
        channel = await client.fetch_channel(channel_id)
    return channel


async def get_guild(client: commands.Bot, guild_id) -> discord.Guild:
    """
    Get guild by calling client. Minimizes API calls.
    :param client:
    :param guild_id:
    :return:
    """
    guild = client.get_guild(guild_id)
    if guild is None:
        guild = await client.fetch_guild(guild_id)
    return guild


async def get_member(client: commands.Bot, member_id, guild_id) -> discord.Member:
    """
    Get member of guild by calling client. Minimizes API calls.
    :param client:
    :param member_id:
    :param guild_id:
    :return:
    """
    guild = await get_guild(client, guild_id)
    member = guild.get_member(member_id)
    if member is None:
        member = await guild.fetch_member(member_id)
    return member


async def get_message_by_id(
    client: commands.Bot, channel_id, message_id
) -> discord.Message:
    """
    Get message by calling client. Minimizes API calls.
    :param client:
    :param channel_id:
    :param message_id:
    :return:
    """
    channel = await get_channel(client, channel_id)
    # print(channel)
    message = await channel.fetch_message(message_id)
    return message


async def remove_role(client: commands.Bot, role_id, member_id):
    """
    Remove role from member by calling client. Minimizes API calls.
    :param client:
    :param role_id:
    :param member_id:
    :return:
    """
    role = await get_role(client, role_id)
    user = await get_member(client, member_id, OI_GUILD_ID)
    await user.remove_roles(role, reason="later timer expired")


def datetime_tz_str_to_datetime(datetime_str):
    """
    Converts datetime string representation i.e. str(datetime obj) to a datetime object.
    :param datetime_str: datetime string in the format "%Y-%m-%d %H:%M:%S.%f%z"
    :return: datetime object representing the datetime string
    """
    format_string = "%Y-%m-%d %H:%M:%S.%f%z"
    return datetime.strptime(datetime_str, format_string)


def id_to_emoji_str(id):
    """
    Converts a cumcry id to an emoji string.
    :param id: user id
    :return: emoji string
    """
    user_dict = db.get_cumcry_id_emoji_pairs()
    return user_dict[id]


def datetime_str_convert_vectorized(str_array):
    """
    Converts an array of string datetime representations to datetime objects.
    :param str_array: Array of strings in the format "%Y-%m-%d %H:%M:%S.%f%z"
    :return: array of datetime objects representing the datetime string
    """
    for i in range(len(str_array)):
        # sanitizes out the time of day for anonymity
        str_array[i] = datetime_tz_str_to_datetime(str_array[i]).replace(hour=0, minute=0, second=0, microsecond=0)

    return str_array


def emoji_str_to_emoji(emoji_str):
    """
    Converts an emoji string to an emoji object.
    :param emoji_str: emoji string
    :return: emoji object
    """
    return emojis.encode(":{}:".format(emoji_str))
