from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_bgg_terraforming_mars(uqcsbot: MockUQCSBot):
    """
    test !bgg terraforming mars
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!bgg terraforming mars')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'].startswith("*Terraforming Mars*\n")
    # 167791 is the BGG ID for Terraforming Mars, and so should appear in the URL
    assert "167791" in messages[-1]['text']
