from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status

from random import choice, randrange

HORROR = ('\u0315', '\u0358', '\u0328', '\u034f', '\u035f', '\u0337', '\u031b', '\u0321', '\u0334',
          '\u035c', '\u0360', '\u0361', '\u0340', '\u0322', '\u0335', '\u035d', '\u0362', '\u0341',
          '\u0327', '\u0336', '\u035e', '\u0338')


@bot.on_command("zalgo")
@loading_status
def handle_zalgo(command: Command):
    """
    `!zalgo TEXT` - Adds Zalgo characters to the given text.
    """
    text = command.arg if command.has_arg() else "Cthulhu fhtagn!"
    response = ""
    for c in text:
        response += c
        for i in range(randrange(7)//3):
            response += choice(HORROR)
    bot.post_message(command.channel_id, response)
