from random import choice
from uqcsbot import bot, Command


@bot.on_command("dice")
def handle_dice(command: Command):
    """
    `!dice [number]` - Rolls 1 or more six sided dice (d6).
    """
    if command.has_arg() and command.arg.isnumeric():
        rolls = min(max(int(command.arg), 1), 360)
    else:
        rolls = 1

    response = []
    emoji = (':dice-one:', ':dice-two:', ':dice-three:',
             ':dice-four:', ':dice-five:', ':dice-six:')
    for i in range(rolls):
        response.append(choice(emoji))

    bot.post_message(command.channel_id, "".join(response))
