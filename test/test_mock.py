from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object

def test_mock(uqcsbot: MockUQCSBot):
    '''
    test !mock
    '''
    message = 'I\'m going to say a really long sentence that has a really low' \
              + ' probability of outputting a random-case mocked message that' \
              + ' is equal to the original.'
    uqcsbot.post_message(TEST_CHANNEL_ID, message)
    mock_call = generate_message_object(TEST_CHANNEL_ID, '!mock')
    # TODO(mitch): add !mock 3 test
    uqcsbot.post_and_handle_command(mock_call)
    channel_messages = uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])
    assert len(channel_messages) == 3
    assert channel_messages[0]['text'].lower() == message.lower()
    assert channel_messages[0]['text'] != message
