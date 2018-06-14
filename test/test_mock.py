from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object

LONG_MESSAGE = 'I\'m going to say a really long sentence that has a really low'\
               + ' probability of outputting a random-case mocked message that'\
               + ' is equal to the original.'

def test_mock_previous_message(uqcsbot: MockUQCSBot):
    '''
    Test !mock on the immediately previous message
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, LONG_MESSAGE)
    mock_call = generate_message_object(TEST_CHANNEL_ID, '!mock')
    uqcsbot.post_and_handle_command(mock_call)
    channel_messages = uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])
    assert len(channel_messages) == 3
    assert channel_messages[0]['text'].lower() == LONG_MESSAGE.lower()
    assert channel_messages[0]['text'] != LONG_MESSAGE

def test_mock_past_message(uqcsbot: MockUQCSBot):
    '''
    Test !mock on a message from the past
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, LONG_MESSAGE)
    uqcsbot.post_message(TEST_CHANNEL_ID, 'just')
    uqcsbot.post_message(TEST_CHANNEL_ID, 'some')
    uqcsbot.post_message(TEST_CHANNEL_ID, 'message')
    uqcsbot.post_message(TEST_CHANNEL_ID, 'padding')
    mock_call = generate_message_object(TEST_CHANNEL_ID, '!mock 4')
    uqcsbot.post_and_handle_command(mock_call)
    channel_messages = uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])
    assert len(channel_messages) == 7
    assert channel_messages[0]['text'].lower() == LONG_MESSAGE.lower()
    assert channel_messages[0]['text'] != LONG_MESSAGE
