from argparse import ArgumentParser
from enum import Enum
from typing import Optional, Tuple

from slackblocks import Attachment, Color, SectionBlock
from sqlalchemy.exc import NoResultFound

from uqcsbot import bot, Command
from uqcsbot.models import Link
from uqcsbot.utils.command_utils import loading_status


class SetResult(Enum):
    """
    Possible outcomes of the set link operation.
    """
    NEEDS_OVERRIDE = "Link already exists, use `-o` to override"
    OVERRIDE_SUCCESS = "Successfully overrode link"
    NEW_LINK_SUCCESS = "Successfully added link"


def set_link_value(key: str, value: str, channel: str,
                   channel_flag: bool, override: bool) -> Tuple[SetResult, str]:
    """
    Sets a corresponding value for a particular key. Keys are set to global by default but this can
    be overridden by passing the channel flag. Existing links can only be overridden if the
    override flag is passed.
    :param key: the lookup key for users to search the value by
    :param value: the value to associate with the key
    :param channel: the name of the channel the set operation was initiated in
    :param channel_flag: required to be True if the association is to be specific to the channel
    :param override: required to be True if an association already exists and needs to be updated
    :return: a SetResult status and the value associated with the given key/channel combination
    """
    link_channel = channel if channel_flag else None
    session = bot.create_db_session()

    try:
        exists = session.query(Link).filter(Link.key == key,
                                            Link.channel == link_channel).one()
        if exists and not override:
            return SetResult.NEEDS_OVERRIDE, exists.value
        exists.value = value
        session.commit()
        return SetResult.OVERRIDE_SUCCESS, exists.value
    except NoResultFound:
        session.add(Link(key=key, channel=link_channel, value=value))
        session.commit()
        return SetResult.NEW_LINK_SUCCESS, value


def get_link_value(key: str, channel: str, global_flag: bool, channel_flag: bool) -> Optional[str]:
    """
    Gets the value associated with a given key (and optionally channel). If a channel association
    exists, this is returned, otherwise a global association is returned. If no association exists
    then None is returned. The default behaviour can be overridden by passing the global flag to
    force retrieval of a global association when a channel association exists.
    :param key: the key to look up
    :param channel: the name of the channel the lookup request was made from
    :param global_flag: required to be True if the global association is requested
    :param channel_flag: required to be True if the channel associate is requested
    :return: the associated value if an association exists, else None
    """
    session = bot.create_db_session()
    channel_match = session.query(Link).filter(Link.key == key,
                                               Link.channel == channel).one_or_none()
    global_match = session.query(Link).filter(Link.key == key,
                                              Link.channel == None).one_or_none()
    if global_flag:
        return global_match.value if global_match else None

    if channel_flag:
        return channel_match.value if channel_match else None

    if channel_match:
        return global_match.value

    if global_match:
        return global_match.value

    return None


@bot.on_command('link')
@loading_status
def handle_link(command: Command) -> None:
    """
    `!link [-c | -g | -o] <key> [value]` - Set and retrieve information in a key value store.
    Links can be set to be channel specific or global. Links are set as global by default, and
    channel specific links are retrieved by default unless overridden with the respective flag.
    """
    parser = ArgumentParser("!link", add_help=False)
    parser.add_argument("key", type=str, help="Lookup key")
    parser.add_argument("value", type=str, help="Value to associate with key", nargs="+")
    flag_group = parser.add_mutually_exclusive_group()
    flag_group.add_argument("-c", "--channel", action="store_true", dest="channel_flag",
                            help="Ensure a channel link is retrieved, or none is")
    flag_group.add_argument("-g", "--global", action="store_true", dest="global_flag",
                            help="Ignore channel link and force retrieval of global")
    parser.add_argument("-o", "--override", action="store_true")

    args = parser.parse_args(command.arg.split() if command.has_arg() else [])
    channel = bot.channels.get(command.channel_id, use_cache=False)

    # Incorrect Usage
    if not args.key:
        bot.post_message(attachments=[Attachment(SectionBlock(parser.format_help()),
                                                 color=Color.WARNING)._resolve()])

    # Retrieve a link
    if not args.value:
        link_value = get_link_value(args.key, channel, args.global_flag, args.channel_flag)
        response = f"{args.key}: {link_value}" if link_value else f"No link found"
        color = Color.GOOD if link_value else Color.DANGER
        attachment = Attachment(SectionBlock(response), color=color)
        return bot.post_message(channel, attatchments=[attachment])

    # Set a link
    if args.key and args.value:
        result, current_value = set_link_value(key=args.key,
                                               channel=channel,
                                               value=args.value,
                                               channel_flag=args.channel_flag,
                                               override=args.override)
        color = Color.DANGER if result == SetResult.NEEDS_OVERRIDE else Color.GOOD
        response = f"{result}: {args.key} ({channel if args.channel_flag else 'global'}) = " \
                   f"{current_value}"
        attachment = Attachment(SectionBlock(response), color=color)
        bot.post_message(channel, f"{result.value}:", attachments=[attachment])
