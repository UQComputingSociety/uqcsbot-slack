from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_voteythumbs(uqcsbot: MockUQCSBot):
    '''
    Tests !voteythumbs
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, '!voteythumbs ye/na/maybz?')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    # Make sure there are three reactions (thumbsup, thumbsdown, eyes)
    assert len(messages[-1]['reactions']) == 3
