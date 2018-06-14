from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object

# TODO(mitch): work out a way to get the dog from dog.py without triggering
# 'on_command' to be called and add '!dog' as a handler which messes with
# testing.

def test_dog(uqcsbot: MockUQCSBot):
    '''
    test !dog
    '''
    message = generate_message_object(TEST_CHANNEL_ID, '!dog')
    uqcsbot.post_and_handle_command(message)
    assert len(uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])) == 2
