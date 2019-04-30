from random import choice
from uqcsbot import bot, Command

@bot.on_command("coin")
def handle_coin(command: Command):
    """
    `!coin [number]` - Flips 1 or more coins.
    """
    if command.has_arg() and command.arg.isnumeric():
        flips = min(max(int(command.arg), 1), 500)
    else:
        flips = 1

    response = []
    emoji = (':heads:', ':tails:')
    for i in range(flips):
        response.append(choice(emoji))

    bot.post_message(command.channel_id, "".join(response))
