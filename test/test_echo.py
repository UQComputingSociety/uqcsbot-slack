from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object

def test_echo(uqcsbot: MockUQCSBot):
    '''
    Test !echo
    '''
    message = generate_message_object(TEST_CHANNEL_ID, '!echo Hello, World!')
    uqcsbot.post_and_handle_command(message)
    channel_messages = uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])
    assert len(channel_messages) == 2
    assert channel_messages[0]['text'] == 'Hello, World!'
