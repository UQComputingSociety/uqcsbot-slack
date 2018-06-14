from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object

def test_echo(uqcsbot: MockUQCSBot):
    '''
    Test !echo
    '''
    message = generate_message_object(TEST_CHANNEL_ID, '!echo Hello, World!')
    uqcsbot.post_and_handle_message(message)
    channel = uqcsbot.test_channels.get(TEST_CHANNEL_ID)
    assert channel is not None
    messages = channel.get('messages', [])
    assert len(messages) == 2
    assert messages[-1]['text'] == 'Hello, World!'
