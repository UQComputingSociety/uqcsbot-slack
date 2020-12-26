from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_uptime(uqcsbot: MockUQCSBot):
    """
    test !uptime for response
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!uptime')
    assert len(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])) == 2
