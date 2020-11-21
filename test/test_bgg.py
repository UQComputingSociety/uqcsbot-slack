from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_bgg_terraforming_mars(uqcsbot: MockUQCSBot):
    """
    test !bgg terraforming mars
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!bgg terraforming mars')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'].startswith("*<https://boardgamegeek.com/boardgame/167791"
                                           + "|Terraforming Mars>*\n")
