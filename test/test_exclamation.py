from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch
from typing import Mapping, TypeVar, Any

T = TypeVar('T', bound=Mapping[str, Any])


@patch("uqcsbot.scripts.yelling.is_human", new=lambda chan: True)
def test_nothing(uqcsbot: MockUQCSBot):
    """
    test with no reply
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "test! string")
    assert len(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])) == 1


@patch("uqcsbot.scripts.yelling.is_human", new=lambda chan: True)
def test_guaranteed(uqcsbot: MockUQCSBot):
    """
    test with guaranteed reply
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "test!!!!!!!!! string")
    assert len(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])) == 2


@patch("uqcsbot.scripts.yelling.is_human", new=lambda chan: True)
def test_possible(uqcsbot: MockUQCSBot):
    """
    test with 50/50 chance of reply
    """
    n = 10
    for i in range(n):
        uqcsbot.post_message(TEST_CHANNEL_ID, "test!!!!!! string")
    assert n < len(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])) < 2*n


@patch("uqcsbot.scripts.yelling.is_human", new=lambda chan: True)
def test_multiple(uqcsbot: MockUQCSBot):
    """
    test with multiple sets
    """
    n = 10
    for i in range(n):
        uqcsbot.post_message(TEST_CHANNEL_ID, "test!!! multiple!!! sets!!!! string")
    assert n < len(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])) < 2*n
