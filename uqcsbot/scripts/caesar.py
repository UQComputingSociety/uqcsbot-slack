import re
from uqcsbot import bot

CAESAR_REGEX = re.compile('!caesar(|-?\d+) (.+)')


@bot.on('message')
def handle_caesar(message: dict):
    '''
    `!caesar[N] <TEXT>` - Performs caesar shift with a left shift of N on given
    text. If unspecified, will shift by 47.
    '''
    text = message.get("text")
    if message.get("subtype") == "bot_message" or text is None:
        return
    m = CAESAR_REGEX.match(text)
    if not m:
        return
    n, msg = m.groups()
    shift = 47 if n == "" else int(n)
    result = ""
    for c in msg:
        # 32 (SPACE) to 126 (~)
        # Get ascii code - 32. This makes SPACE the equivalent of 0
        # + n. Add caesar shift
        # mod 94 (from 126-32=94). This prevents overflow
        # + 32. Changes back (so SPACE is back to 32 instead of 0)
        char_code = ord(c) - 32 + shift
        char_code = ((char_code % 94) + 94) % 94
        char_code += 32
        result += chr(char_code)
    bot.post_message(message['channel'], result)
