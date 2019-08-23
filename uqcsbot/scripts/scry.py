from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status

from urllib.request import urlopen
from urllib.error import HTTPError
from json import loads


@bot.on_command('scry')
@loading_status
def handle_scry(command: Command) -> None:
    """
    `!scry [name]` - Returns the Magic: the Gathering card that matches (partially
    or fully) the given argument (or a random card if no argument given)
    """

    # random card if no argument
    if command.has_arg():
        request = "https://api.scryfall.com/cards/named?fuzzy=" + command.arg.replace(' ', '+')
    else:
        request = "https://api.scryfall.com/cards/random"

    # try find card
    try:
        response = urlopen(request)
    except HTTPError as e:
        # will 404 if cannot find a unique result
        if e.code == 404:
            fault = loads(e.read())
            if fault.get('type') == "ambiguous":
                bot.post_message(command.channel_id, "Request 404'd; Multiple Possible Cards")
            else:
                bot.post_message(command.channel_id, "Request 404'd; No Cards Found")
            return
        bot.post_message(command.channel_id, str(e))
        return

    card = loads(response.read())
    if 'image_uris' in card:
        # single faced cards
        bot.post_message(command.channel_id, card['image_uris']['png'])
    else:
        # double faced cards
        for face in card['card_faces']:
            bot.post_message(command.channel_id, face['image_uris']['png'])
