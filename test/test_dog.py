from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object

def test_dog(uqcsbot: MockUQCSBot):
    '''
    test !dog
    '''
    message = generate_message_object(TEST_CHANNEL_ID, '!dog')
    uqcsbot.post_and_handle_command(message)
    assert len(uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])) == 2
