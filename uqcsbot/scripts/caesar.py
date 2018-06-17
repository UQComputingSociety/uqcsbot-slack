import argparse
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
    arg_parser.add_argument('-n', type=int, default=47)
    arg_parser.add_argument('text')

    parsed_args = arg_parser.parse_args(command_args)
    message = ''
    for char in parsed_args.text:
        # 32 (SPACE) to 126 (~)
        # Get ascii code - 32. This makes SPACE the equivalent of 0
        # + n. Add caesar shift
        # mod 94 (from 126-32=94). This prevents overflow
        # + 32. Changes back (so SPACE is back to 32 instead of 0)
        char_code = ord(char) - 32 + parsed_args.n
        char_code = ((char_code % 94) + 94) % 94
        char_code += 32
        message += chr(char_code)
    bot.post_message(command.channel_id, message)
