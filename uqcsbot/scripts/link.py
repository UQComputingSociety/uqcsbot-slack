from argparse import ArgumentParser
from enum import Enum
from typing import Optional, Tuple

from slackblocks import Attachment, Color, SectionBlock
from sqlalchemy.exc import NoResultFound

from uqcsbot import bot, Command
from uqcsbot.models import Link
from uqcsbot.utils.command_utils import loading_status


class SetResult(Enum):
    NEEDS_OVERRIDE = "Value exists"
    OVERRIDE_SUCCESS = "Successfully overrode link"
    NEW_LINK_SUCCESS = "Successfully added link"


def set_link_value(key: str, value: str, channel: str, global_flag: bool,
                   channel_flag: bool, override: bool) -> Tuple[SetResult, str]:
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
    session = bot.create_db_session()
    channel_match = session.query(Link).filter(Link.key == key,
                                               Link.channel == channel).one_or_none()
    global_match = session.query(Link).filter(Link.key == key,
                                              Link.channel == None).one_or_none()
    if global_flag:
        if global_match:
            return global_match.value
        else:
            return None

    if channel_flag and channel_match:
        if channel_match:
            return channel_match.value
        else:
            return None

    if global_match:
        return global_match.value

    if channel_match:
        return global_match.value

    return None


@bot.on_command('link')
@loading_status
def handle_link(command: Command) -> None:
    parser = ArgumentParser("!link", add_help=False)
    parser.add_argument("key", type=str, help="Lookup key")
    parser.add_argument("value", type=str, help="Lookup key")
    parser.add_argument("-c", "--channel", action="store_true", dest="channel_flag")
    parser.add_argument("-g", "--global", action="store_true", dest="global_flag",
                        help="Ignore channel link and force retrieval of global")
    parser.add_argument("-o", "--override", action="store_true")

    args = parser.parse_args(command.arg.split() if command.has_arg() else [])
    channel = bot.channels.get(command.channel_id, use_cache=False)

    if not args.key:
        bot.post_message(attachments=[Attachment(SectionBlock(parser.format_help()),
                                                 color=Color.WARNING)._resolve()])

    if not args.value:
        link_value = get_link_value(args.key, channel, args.global_flag, args.channel_flag)
        response = f"{args.key}: {link_value}" if link_value else f"No link found"
        return bot.post_message(channel, response)

    if args.key and args.value:
        result, current_value = set_link_value(key=args.key,
                                               channel=channel,
                                               value=args.value,
                                               channel_flag=args.channel_flag,
                                               global_flag=args.global_flag,
                                               override=args.override)
        bot.post_message(channel, f"{result}: {args.key} ({channel if args.channel_flag else 'global'}) = {current_value}")
