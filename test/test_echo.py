from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object

def test_echo(uqcsbot: MockUQCSBot):
    '''
    Test !echo
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, '!echo Hello, World!')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == 'Hello, World!'
