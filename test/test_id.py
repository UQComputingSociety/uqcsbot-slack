from test.conftest import MockUQCSBot, TEST_CHANNEL_ID, TEST_BOT_ID


def test_id(uqcsbot: MockUQCSBot):
    '''
    Test !id
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, '!id')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == f'`{TEST_BOT_ID}`'
