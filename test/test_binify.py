from random import choice
from test.conftest import MockUQCSBot, TEST_CHANNEL_ID

BINARY_STRING = ("01110011011110010111001101110100011001010110110101011111"
                 + "01100101011100100100010001001001010001010111001001101111"
                 + "01110010010001000100100101000101010001000100100101000101"
                 + "010001000100100101000101")
ASCII_STRING = "system_erDIErorDIEDIEDIE"


def test_binify_from_binary(uqcsbot: MockUQCSBot):
    """
    Test !binify for a binary string input
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!binify " + BINARY_STRING)
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == ASCII_STRING


def test_binify_from_ascii(uqcsbot: MockUQCSBot):
    """
    Test !binify for an ascii string input
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!binify " + ASCII_STRING)
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == BINARY_STRING


def test_binify_cyclic(uqcsbot: MockUQCSBot):
    """
    Test !binify twice in a row returns original string
    """
    message = "".join([choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                       for i in range(32)])
    uqcsbot.post_message(TEST_CHANNEL_ID, "!binify " + message)
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    response = messages[-1]['text']
    uqcsbot.post_message(TEST_CHANNEL_ID, "!binify " + response)
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert messages[-1]['text'] == message


def test_binify_out_of_range(uqcsbot: MockUQCSBot):
    """
    Test !binify for a character code 128+
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!binify 11110000")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "Character out of ascii range (0-127)"


def test_binify_incomplete(uqcsbot: MockUQCSBot):
    """
    Test !binify for patial byte
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!binify 01010")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "Binary string contains partial byte."


def test_binify_no_argument(uqcsbot: MockUQCSBot):
    """
    Test !binify for missing argument
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!binify")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "Please include string to convert."
