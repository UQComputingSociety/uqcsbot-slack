from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_numbers(uqcsbot: MockUQCSBot):
    """
    Test !pokemash with numeric arguments.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!pokemash 1 4')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == ("_Bulbmander_\n"
                                    "https://images.alexonsager.net/pokemon/fused/4/4.1.png")


def test_names(uqcsbot: MockUQCSBot):
    """
    Test !pokemash with name arguments.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!pokemash mr. mime scyther')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == ("_Mr.ther_\n"
                                    "https://images.alexonsager.net/pokemon/fused/123/123.122.png")


def test_count(uqcsbot: MockUQCSBot):
    """
    Test !pokemash with too many numbers.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!pokemash 1 4 7')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == ("Incorrect Number of Pokemon")


def test_misname(uqcsbot: MockUQCSBot):
    """
    Test !pokemash with bad name.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!pokemash mew lucario')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == ("Could Not Find Pokemon: lucario")


def test_negative(uqcsbot: MockUQCSBot):
    """
    Test !pokemash negative number.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!pokemash 25 -25')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == ("Out of Range: -25")
