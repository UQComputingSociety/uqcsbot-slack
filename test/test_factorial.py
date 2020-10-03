from test.conftest import MockUQCSBot, TEST_CHANNEL_ID, TEST_USER_ID


def test_factorial_basic(uqcsbot: MockUQCSBot):
    """
    test basic factorial
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "8!", user=TEST_USER_ID)
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    for i in messages:
        print(i['user'])
    assert len(messages) == 2
    assert messages[-1]['text'] == "8! = 40320"


def test_factorial_words(uqcsbot: MockUQCSBot):
    """
    test factorial with surrounding words
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "blah 8! blah", user=TEST_USER_ID)
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "8! = 40320"


def test_factorial_multiline(uqcsbot: MockUQCSBot):
    """
    test factorial with multiple lines
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "blah\n8!\n blah", user=TEST_USER_ID)
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "8! = 40320"


def test_multiple_factorials(uqcsbot: MockUQCSBot):
    """
    test multiple factorials in one string
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "8! 10!", user=TEST_USER_ID)
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "8! = 40320\n10! = 3628800"


def test_double_factorial(uqcsbot: MockUQCSBot):
    """
    test with double factorial
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "8!!", user=TEST_USER_ID)
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "8!! = 384"


def test_large_factorial(uqcsbot: MockUQCSBot):
    """
    test factorial with a large number
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "65536!", user=TEST_USER_ID)
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "65536! ≈ ∞"
