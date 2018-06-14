from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object

# TODO(mitch): work out a way to get the cat from cat.py without triggering
# 'on_command' to be called and add '!cat' as a handler which messes with
# testing.

def test_cat(uqcsbot: MockUQCSBot):
    '''
    test !cat
    '''
    message = generate_message_object(TEST_CHANNEL_ID, '!cat')
    uqcsbot.post_and_handle_command(message)
    channel_messages = uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])
    assert len(channel_messages) == 2
