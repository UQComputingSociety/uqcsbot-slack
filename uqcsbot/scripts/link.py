from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status

from argparse import ArgumentParser
from slackblocks import Attachment, Color, SectionBlock


def get_link_value(key: str, channel: str, global_: bool) -> str:
    pass


@bot.on_command('link')
@loading_status
def handle_link(command: Command) -> None:
    parser = ArgumentParser("!link", add_help=False)
    parser.add_argument("key", type=str, help="Lookup key")
    parser.add_argument("value", type=str, help="Lookup key")
    parser.add_argument("-c", "--channel", action="store_true")
    parser.add_argument("-g", "--global", action="store_true", dest="global_",
                        help="Ignore channel link and force retrieval of global")
    parser.add_argument("-o", "--override", action="store_true")

    args = parser.parse_args(command.arg.split() if command.has_arg() else [])
    channel = bot.channels.get(command.channel_id, use_cache=False)

    if not args.key:
        bot.post_message(attachments=[Attachment(SectionBlock(parser.format_help()),
                                                 color=Color.WARNING)._resolve()])

    if not args.value:
        link_value = get_link_value(args.key, args.channel, args.global_)
        response = f"{args.key}: {link_value}" if link_value else f"No link found"
        return bot.post_message(channel, response)

