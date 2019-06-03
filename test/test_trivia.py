from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_trivia_multiple(uqcsbot: MockUQCSBot):
    """
    Tests !trivia with the multiple choice option
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!trivia -t multiple')
    uqcsbot.post_message(TEST_CHANNEL_ID, '!trivia --type multiple')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])

    assert len(messages) == 6


def test_trivia_boolean(uqcsbot: MockUQCSBot):
    """
        Tests !trivia with the true/false option
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!trivia -t boolean')
    uqcsbot.post_message(TEST_CHANNEL_ID, '!trivia --type boolean')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])

    assert len(messages) == 4


def test_bad_input(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!trivia -d easp")
    uqcsbot.post_message(TEST_CHANNEL_ID, "!trivia -c -22")
    uqcsbot.post_message(TEST_CHANNEL_ID, "!trivia -t raspberry")

    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])

    assert len(messages) == 6
