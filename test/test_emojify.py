from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_emojify_count(uqcsbot: MockUQCSBot):
    '''
    Ensure !emojify returns the correct number of emoji
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, '!emojify abc 123')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]["text"].count(':') == 14


def test_emojify_z(uqcsbot: MockUQCSBot):
    '''
    Ensure !emojify returns the correct emoji
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, '!emojify zzz')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]["text"] == ":tetris_z::tetris_z::tetris_z:"
