import argparse
import string
from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import UsageSyntaxException


@bot.on_command('caesar')
def handle_caesar(command: Command):
    '''
    `!caesar [<-n> <NUM_SHIFT>] <TEXT>` - Performs caesar shift with a left
    shift of NUM_SHIFT on the given text. If NUM_SHIFT is unspecified, will
    shift by 47.
    '''
    command_args = command.arg.split() if command.has_arg() else []

    arg_parser = argparse.ArgumentParser()
    def usage_error(*args, **kwargs):
        raise UsageSyntaxException()
    arg_parser.error = usage_error  # type: ignore
    arg_parser.add_argument('-n', default=47, type=int)
    arg_parser.add_argument('text')

    parsed_args = arg_parser.parse_args(command_args)
    printable_text = string.printable
    shift_point = parsed_args.n % len(printable_text)
    shifted_text = printable_text[shift_point:] + printable_text[:shift_point]
    trans_table = str.maketrans(printable_text, shifted_text)
    bot.post_message(command.channel_id, parsed_args.text.translate(trans_table))
