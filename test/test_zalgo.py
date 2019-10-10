from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_zalgo(uqcsbot: MockUQCSBot):
    """
    Test !zalgo with text
    """
    phrase = "Hello, World!"
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!zalgo {phrase}")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    response = messages[-1]['text']
    assert len(response) > len(phrase)
    assert "".join(i for i in response if ord(i) < 128) == phrase


def test_zalgo_default(uqcsbot: MockUQCSBot):
    """
    Test !zalgo with no text
    """
    phrase = "Cthulhu fhtagn!"
    uqcsbot.post_message(TEST_CHANNEL_ID, "!zalgo")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    response = messages[-1]['text']
    assert len(response) > len(phrase)
    assert "".join(i for i in response if ord(i) < 128) == phrase
