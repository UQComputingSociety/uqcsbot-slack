import argparse
from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import UsageSyntaxException


@bot.on_command('caesar')
def handle_caesar(command: Command):
    '''
    `!caesar [<-n> <NUM_SHIFT>] <TEXT>` - Performs caesar shift with a left shift
    of N on the given text. If N is unspecified, will shift by 47.
    '''
    command_args = command.arg.split() if command.has_arg() else []

    arg_parser = argparse.ArgumentParser()
    arg_parser.error = UsageSyntaxException
    arg_parser.add_argument('-n')
    arg_parser.add_argument('text')

    parsed_args = arg_parser.parse_args(command_args)
    shift = parsed_args.n if parsed_args.n is not None else 47
    message = ''
    for char in parsed_args.text:
        # 32 (SPACE) to 126 (~)
        # Get ascii code - 32. This makes SPACE the equivalent of 0
        # + n. Add caesar shift
        # mod 94 (from 126-32=94). This prevents overflow
        # + 32. Changes back (so SPACE is back to 32 instead of 0)
        char_code = ord(char) - 32 + shift
        char_code = ((char_code % 94) + 94) % 94
        char_code += 32
        message += chr(char_code)
    bot.post_message(command.channel_id, message)
