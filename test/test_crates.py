from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_crates_exact(uqcsbot: MockUQCSBot):
    """
    Tests !crates with an exact crate search
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!crates regex')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])

    assert len(messages) == 2


def test_crates_search(uqcsbot: MockUQCSBot):
    """
    Tests !crates search by searching for a specific thing
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!crates search rand -l 2 --sort downloads -c algorithms')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])

    assert len(messages) == 2


def test_categories(uqcsbot: MockUQCSBot):
    """
    Tests the !trivia categories sub command
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!crates categories")
    uqcsbot.post_message(TEST_CHANNEL_ID, "!crates categories algorithms")

    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])

    assert len(messages) == 4
