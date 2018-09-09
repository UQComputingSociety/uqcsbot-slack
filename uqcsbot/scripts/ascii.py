from uqcsbot import bot, Command
from requests import get
from requests.exceptions import RequestException
from uqcsbot.utils.command_utils import loading_status
import random

NO_QUERY_MESSAGE = "Can't ASCIIfy nothing... try `!asciify <TEXT>`"
BOTH_OPTIONS_MESSAGE = "Font can only be random OR specified"
ERROR_MESSAGE = "Trouble with HTTP Request, can't ASCIIfy :("
NO_FONT_MESSAGE = "Cannot find the specified font in the fontslist."
ASCII_URL = "http://artii.herokuapp.com/make?text="
FONT_URL = "http://artii.herokuapp.com/fonts_list"

@bot.on_command("asciify")
@loading_status
def handle_asciify(command: Command):
    """
    `!asciify [--fontslist] [--randomfont | --<CUSTOM FONT>] <TEXT>` - Returns
    ASCIIfyed text. `--fontslist` also returns a URL to available fonts, `--randomfont`
    returns, well... a random font. A custom font from the fonts list can also be
    specified.
    """
    # Makes sure the query is not empty
    if not command.has_arg():
        bot.post_message(command.channel_id, NO_QUERY_MESSAGE)
        return
    command_args = command.arg.split()
    random_font = False
    custom_font = False
    return_fonts = False
    #check for font list option
    if '--fontslist' in command_args:
        return_fonts = True
        command_args.remove('--fontslist')
    #check for random font option
    if '--randomfont' in command_args:
        random_font = True
        command_args.remove('--randomfont')
    #check for custom font option
    fontslist = get_fontslist()
    if not fontslist:
        bot.post_message(command.channel_id, ERROR_MESSAGE)
        return
    for i in command_args:
        if '--' in i:
            if i.strip('--') in fontslist:
                custom_font = True
                selected_font = i.strip('--')
                command_args.remove(i)
                break
            else:
                bot.post_message(command.channel_id, NO_FONT_MESSAGE)
                return
    #check for invalid options
    if random_font and custom_font:
        bot.post_message(command.channel_id, BOTH_OPTIONS_MESSAGE)
        return
    if not command_args:
        text = None
    else: 
        text = ' '.join(command_args)
    #asciification
    if text is None:
        bot.post_message(command.channel_id, NO_QUERY_MESSAGE)
        ascii_text = None
    else:
        if random_font:
            font = get_random_font()
        elif custom_font:
            font = selected_font
        else:
            font = None
        ascii_text = asciify(text, font)
        if ascii_text is None:
            bot.post_message(command.channel_id, ERROR_MESSAGE)
            return
    #message posts
    if return_fonts:
        bot.post_message(command.channel_id, FONT_URL)
    if ascii_text:
        bot.post_message(command.channel_id, ascii_text)
    else:
        return
    return


def asciify(text: str, font: str) -> str:
    try:
        if font is not None:
            url = ASCII_URL + text + '&font=' + font
        else:
            url = ASCII_URL + text
        resp = get(url)
        ascii_text = f"```\n{resp.text}\n```"
        return ascii_text
    except RequestException as e:
        return None
    

def get_random_font() -> str:
    fontslist = get_fontslist()
    if fontslist:
        return random.choice(tuple(fontslist))
    else:
        return None


def get_fontslist() -> set:
    try:
        resp = get('http://artii.herokuapp.com/fonts_list')
        fontslist = set(resp.text.split())
        return fontslist
    except RequestException as e:
        return None
    
    
