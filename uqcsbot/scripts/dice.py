from random import choice
from uqcsbot import bot, Command

def is_number(message):
    '''
    Tries to coerce the message to an integer. If successful, return True-- else
    returns False.
    '''
    try:
        int(message)
    except:
        return False
    return True


@bot.on_command("dice")
def handle_dice(command: Command):
    '''
    `!dice [number]` - Rolls 1 or more six sided dice (d6).
    '''
    if command.has_arg() and is_number(command.arg):
        num = max(int(command.arg), 1)
    else:
        num = 1

    resp = []
    emoj = (':dice-one:', ':dice-two:', ':dice-three:', ':dice-four:', ':dice-five:', ':dice-six:')
    for i in range(num):
        resp.append(choice(emoj))

    bot.post_message(command.channel_id, "".join(resp))
