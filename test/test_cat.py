from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object
from uqcsbot.scripts.cat import CAT

def test_cat(uqcsbot: MockUQCSBot):
    '''
    test !cat
    '''
    message = generate_message_object(TEST_CHANNEL_ID, '!cat')
    uqcsbot.post_and_handle_command(message)
    assert len(uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])) == 2
