from time import sleep
from typing import Mapping, TypeVar, Generator, Any, List
from unittest.mock import patch

from test.conftest import MockUQCSBot, TEST_CHANNEL_ID, TEST_USER_ID


def count_messages(uqcsbot: MockUQCSBot):
    return len(list(uqcsbot.test_messages.get(TEST_CHANNEL_ID)))


@patch("uqcsbot.scripts.yelling.in_yelling", new=lambda chan: True)
def test_minuscule(uqcsbot: MockUQCSBot):
    """
    test minuscule string
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "wintermute", user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 2


@patch("uqcsbot.scripts.yelling.in_yelling", new=lambda chan: True)
def test_majuscule(uqcsbot: MockUQCSBot):
    """
    test majuscule string
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "WINTERMUTE", user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 1


@patch("uqcsbot.scripts.yelling.in_yelling", new=lambda chan: True)
def test_mixed(uqcsbot: MockUQCSBot):
    """
    test mixed case string
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "wiNTErMUTe", user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 2


@patch("uqcsbot.scripts.yelling.in_yelling", new=lambda chan: False)
def test_channel(uqcsbot: MockUQCSBot):
    """
    tests outside of #yeling
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "wintermute", user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 1


@patch("uqcsbot.scripts.yelling.in_yelling", new=lambda chan: True)
def test_thread_discreet_minuscule(uqcsbot: MockUQCSBot):
    """
    test minuscule string reply to thread
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "NEUROMANCER", user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 1
    thread = float(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])[-1].get('ts', 0))
    uqcsbot.post_message(TEST_CHANNEL_ID, "wintermute",
                         reply_broadcast=False, thread_ts=thread, user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 3


@patch("uqcsbot.scripts.yelling.in_yelling", new=lambda chan: True)
def test_thread_discreet_majuscule(uqcsbot: MockUQCSBot):
    """
    test majuscule string reply to thread
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "NEUROMANCER", user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 1
    thread = float(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])[-1].get('ts', 0))
    uqcsbot.post_message(TEST_CHANNEL_ID, "WINTERMUTE",
                         reply_broadcast=False, thread_ts=thread, user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 2


@patch("uqcsbot.scripts.yelling.in_yelling", new=lambda chan: True)
def test_thread_blatant_minuscule(uqcsbot: MockUQCSBot):
    """
    test minuscule string reply to thread and channel
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "NEUROMANCER", user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 1
    thread = float(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])[-1].get('ts', 0))
    uqcsbot.post_message(TEST_CHANNEL_ID, "wintermute", reply_broadcast=True, thread_ts=thread,
                         user=TEST_USER_ID)
    sleep(1)
    assert count_messages(uqcsbot) == 3


@patch("uqcsbot.scripts.yelling.in_yelling", new=lambda chan: True)
def test_thread_blatant_majuscule(uqcsbot: MockUQCSBot):
    """
    test majuscule string reply to thread and channel
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "NEUROMANCER", user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 1
    thread = float(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])[-1].get('ts', 0))
    uqcsbot.post_message(TEST_CHANNEL_ID, "WINTERMUTE",
                         reply_broadcast=True, thread_ts=thread, user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 2


@patch("uqcsbot.scripts.yelling.in_yelling", new=lambda chan: True)
def test_url(uqcsbot: MockUQCSBot):
    """
    Test that URLs are not detected as talking quietly.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "Hoogle", user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 2
    uqcsbot.post_message(TEST_CHANNEL_ID, "hoogle.haskell.org/", user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 3
    thread = float(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])[-1].get('ts', 0))
    uqcsbot.post_message(TEST_CHANNEL_ID, "https://google.com",
                         reply_broadcast=True,
                         thread_ts=thread,
                         user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 4
    uqcsbot.post_message(TEST_CHANNEL_ID, "<https://google.com|google.com>", user=TEST_USER_ID)
    assert count_messages(uqcsbot) == 5
