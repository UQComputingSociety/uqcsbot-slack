from uqcsbot import Command
from test.conftest import MockUQCSBot, TEST_CHANNEL_ID

def test_trivia(uqcsbot: MockUQCSBot):
    """
    Tests !trivia
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!trivia')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])

    assert len(messages) == 3 or len(messages) == 2
