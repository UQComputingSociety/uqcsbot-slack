"""
Utilities for modifying messages.
"""

from uqcsbot import bot
import re


def insert_channel_links(message: str) -> str:
    """
    Takes a message and replaces all of the channel references with
    links to those channels in Slack formatting.
    :param message: The message to modify
    :return: A modified copy of the message
    """
    message_with_links = message
    matches = re.findall(r'#[a-z0-9\-_(){}\[\]\'\"/]{1,22}', message)
    for match in matches:
        channel_name = match[1:]
        channel = bot.channels.get(channel_name)
        if channel is not None:
            channel_link_string = f"<#{channel.id}|{channel.name}>"
            message_with_links = message_with_links.replace(match, channel_link_string)
    return message_with_links
