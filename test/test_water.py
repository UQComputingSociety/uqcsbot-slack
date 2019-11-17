from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
import re

def test_water_valid_message(uqcsbot: MockUQCSBot):
    """
    Test !water <REGION> returns a reading
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!water SEQ')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert re.compile(r"(?:.*) is at \*\d+\.\d+\%\* \((?:.*?)ML of (?:.*?)ML\)").match(messages[-1]['text'])

def test_water_invalid_region(uqcsbot: MockUQCSBot):
    """
    Test !water <INVALID_REGION> returns a warning
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!water abcdefghijklmnopqrstuvwxyz')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert re.compile(r"No region or alias found matching '(?:.*?)'").match(messages[-1]['text'])

def test_water_list(uqcsbot: MockUQCSBot):
    """
    Test !water <LIST> returns a listing
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!water list')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert re.compile(r"Available regions:(.*)").match(messages[-1]['text'])