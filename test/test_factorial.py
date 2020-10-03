from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch


@patch("uqcsbot.scripts.factorial.is_human", new=lambda user: True)
def test_factorial_basic(uqcsbot: MockUQCSBot):
    """
    test basic factorial
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "8!")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "8! = 40320"


@patch("uqcsbot.scripts.factorial.is_human", new=lambda user: True)
def test_factorial_words(uqcsbot: MockUQCSBot):
    """
    test factorial with surrounding words
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "blah 8! blah")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "8! = 40320"


@patch("uqcsbot.scripts.factorial.is_human", new=lambda user: True)
def test_factorial_multiline(uqcsbot: MockUQCSBot):
    """
    test factorial with multiple lines
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "blah\n8!\n blah")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "8! = 40320"


@patch("uqcsbot.scripts.factorial.is_human", new=lambda user: True)
def test_multiple_factorials(uqcsbot: MockUQCSBot):
    """
    test multiple factorials in one string
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "8! 10!")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "8! = 40320\n10! = 3628800"


@patch("uqcsbot.scripts.factorial.is_human", new=lambda user: True)
def test_double_factorial(uqcsbot: MockUQCSBot):
    """
    test with double factorial
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "8!!")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == "8!! = 384"
