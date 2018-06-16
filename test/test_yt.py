"""
Tests for yt.py
"""
from test.conftest import MockUQCSBot, TEST_CHANNEL_ID

YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v='
# TODO(mitch): work out a way to get this from yt.py without triggering
# 'on_command' to be called and add '!yt' as a handler which messes with
# testing.
NO_QUERY_MESSAGE = "You can't look for nothing. !yt <QUERY>"

def test_yt_no_query(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!yt")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == NO_QUERY_MESSAGE

def test_yt_normal(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!yt dog")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'][0:len(YOUTUBE_VIDEO_URL)] == YOUTUBE_VIDEO_URL
