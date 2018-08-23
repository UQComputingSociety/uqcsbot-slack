"""
Tests for ascii.py
"""
from test.conftest import MockUQCSBot, TEST_CHANNEL_ID

TEST_TEXT = "ThIS iS a TeST MesSAgE"
FONTSLIST_URL = "http://artii.herokuapp.com/fonts_list"

NO_QUERY_MESSAGE = "Can't ASCIIfy nothing... try `!asciify <TEXT>`"
BOTH_OPTIONS_MESSAGE = "Font can only be random OR specified"
ERROR_MESSAGE = "Trouble with HTTP Request, can't ASCIIfy :("

DEFAULT_FONT_RESULT= '''  _______ _     _____  _____   _  _____           _______    _____ _______   __  __           _____              ______ 
 |__   __| |   |_   _|/ ____| (_)/ ____|         |__   __|  / ____|__   __| |  \/  |         / ____|  /\        |  ____|
    | |  | |__   | | | (___    _| (___     __ _     | | ___| (___    | |    | \  / | ___ ___| (___   /  \   __ _| |__   
    | |  | '_ \  | |  \___ \  | |\___ \   / _` |    | |/ _ \\___ \   | |    | |\/| |/ _ \ __|\___ \ / /\ \ / _` |  __|  
    | |  | | | |_| |_ ____) | | |____) | | (_| |    | |  __/____) |  | |    | |  | |  __\__ \____) / ____ \ (_| | |____ 
    |_|  |_| |_|_____|_____/  |_|_____/   \__,_|    |_|\___|_____/   |_|    |_|  |_|\___|___/_____/_/    \_\__, |______|

                                                                                                          __/ |       
                                                                                                           |___/        '''
CUSTOM_FONT_RESULT= ''' ######           ####  #####          #####            ######          ##### ######   #     #                  #####   ##           ######   
 # ## #  #   #     ##  ### ##     ##  ### ##     ##     # ## #  # #### ### ## # ## #   ##   ##  # ####  ###### ### ##  ####    # #### ##  ##  
   ##    #   #     ##  ###       ###  ###       # #       ##    #   ## ###      ##     ### ###  #   ## ##   ## ###    ##  ##  ##   ## ##      
   ##    #   #     ##   ####      ##   ####    ## #       ##    #       ####    ##     #######  #      ##       ####  ##  ##  ##      ####    
   ##   #######    ##     ###    ###     ###   #  ##      ##   ## ##      ###   ##     ## # ## ## ##    #####     ### ######  #       ##      
   ##   ##   ##    ##  ## ###    ###  ## ###  ## ####     ##   ##      ## ###   ##     ##   ## ##           ## ## ### ##  ##  #   ### ##  ##  
  ####  ##   ##   #### #####      ##  #####   ##   ##    ####  ##  ### #####   ####    ##   ## ##  ### ##   ## ##### ##    ## ###  # ######   
         #   ##                   ##          ##   ##          ## ###                          ## ###  ### ##                  #####          '''

def test_default_font(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!asciify {TEST_TEXT}")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == DEFAULT_FONT_RESULT

def test_custom_font(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!asciify --demo_2__ {TEST_TEXT}")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert print(messages[1].get('text')) == CUSTOM_FONT_RESULT


def test_get_fontslist(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!asciify --fontslist")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == FONTSLIST_URL

def test_invalid_options(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!asciify --randomfont --demo_2__")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == BOTH_OPTIONS_MESSAGE



