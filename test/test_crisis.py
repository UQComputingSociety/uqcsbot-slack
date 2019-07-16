from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_crisis_keyword(uqcsbot: MockUQCSBot):
    """
    Ensure !crisis returns the intended resource
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!crisis')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert "campus security" in messages[-1]['text'].lower()


def test_mentalhealth_keyword(uqcsbot: MockUQCSBot):
    """
    Ensure !mentalhealth also returns the intended resource
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!mentalhealth')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert "campus security" in messages[-1]['text'].lower()


def test_emergency_keyword(uqcsbot: MockUQCSBot):
    """
    Ensure !emergency also does the needful
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!emergency')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert "campus security" in messages[-1]['text'].lower()
