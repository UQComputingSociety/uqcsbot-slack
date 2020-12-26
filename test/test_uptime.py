from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_uptime(uqcsbot: MockUQCSBot):
    """
    test !uptime for response
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!uptime')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]["text"].startswith("The bot has been online for")
