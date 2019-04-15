import os
from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import UsageSyntaxException

AVAILABLE_CODES = {
    100, 101, 200, 201, 202, 204, 206, 207, 300, 301, 302, 303, 304, 305, 307,
    400, 401, 402, 403, 404, 405, 406, 408, 409, 410, 411, 412, 413, 414, 415,
    416, 417, 418, 420, 421, 422, 423, 424, 425, 426, 429, 431, 444, 450, 451,
    500, 502, 503, 504, 506, 507, 508, 509, 510, 511, 599,
}


@bot.on_command('http')
def handle_http(command: Command):
    '''
    `!http <CODE>` - Returns a HTTP cat.
    '''
    if not command.has_arg():
        raise UsageSyntaxException()

    try:
        http_code = int(command.arg.strip())
    except ValueError as e:
        raise UsageSyntaxException()

    if http_code not in AVAILABLE_CODES:
        bot.post_message(command.channel_id, f'HTTP cat {http_code} is not available')
        return

    bot.post_message(command.channel_id, f'https://http.cat/{http_code}')
