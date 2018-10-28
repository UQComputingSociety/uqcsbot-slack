"""
Tests for ascii.py
"""
from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch


TEST_TEXT = "ThIS iS a TeST MesSAgE"
FONT_URL = "http://artii.herokuapp.com/fonts_list"
NO_QUERY_MESSAGE = "Can't ASCIIfy nothing... try `!asciify <TEXT>`"
BOTH_OPTIONS_MESSAGE = "Font can only be random OR specified"
ERROR_MESSAGE = "Trouble with HTTP Request, can't ASCIIfy :("
NO_FONT_MESSAGE = "Cannot find the specified font in the fontslist."


def mocked_get_fontslist(*args, **kwargs):
    '''
    Mocks get fontslist by retuning a local file containing fonts for
    offline testing
    '''
    with open('test/fontslist.txt', 'r') as file:
        content = file.readlines()
        fontslist = []
        for i in content:
            fontslist.append(i.strip())
    return fontslist


def mocked_asciify(text, font):
    '''
    Mocks ascii art API response, returns DEFAULT_FONT if called without
    a custom font, returns CUSTOM_FONT if called with a custom font
    '''
    if font is not None:
        return f"CUSTOM_FONT {font}"
    else:
        return "DEFAULT_FONT"


@patch("uqcsbot.scripts.ascii.asciify", new=mocked_asciify)
@patch("uqcsbot.scripts.ascii.get_fontslist", new=mocked_get_fontslist)
def test_default_font(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!asciify {TEST_TEXT}")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == 'DEFAULT_FONT'


@patch("uqcsbot.scripts.ascii.asciify", new=mocked_asciify)
@patch("uqcsbot.scripts.ascii.get_fontslist", new=mocked_get_fontslist)
def test_custom_font(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!asciify --demo_2__ {TEST_TEXT}")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == 'CUSTOM_FONT demo_2__'


@patch("uqcsbot.scripts.ascii.get_fontslist", new=mocked_get_fontslist)
def test_return_fontslist(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!asciify --fontslist")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 3
    assert messages[2].get('text') == FONT_URL


@patch("uqcsbot.scripts.ascii.asciify", new=mocked_asciify)
@patch("uqcsbot.scripts.ascii.get_fontslist", new=mocked_get_fontslist)
def test_invalid_options(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!asciify --randomfont --demo_2__")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == BOTH_OPTIONS_MESSAGE


@patch("uqcsbot.scripts.ascii.asciify", new=mocked_asciify)
@patch("uqcsbot.scripts.ascii.get_fontslist", new=mocked_get_fontslist)
def test_random_font(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!asciify --randomfont {TEST_TEXT}")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    fontslist = mocked_get_fontslist()
    assert len(messages) == 2
    assert messages[1].get('text').split()[0] == "CUSTOM_FONT"
    assert messages[1].get('text').split()[1] in fontslist


@patch("uqcsbot.scripts.ascii.asciify", new=mocked_asciify)
@patch("uqcsbot.scripts.ascii.get_fontslist", new=mocked_get_fontslist)
def test_invalid_font(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!asciify --invalidfont {TEST_TEXT}")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == NO_FONT_MESSAGE
