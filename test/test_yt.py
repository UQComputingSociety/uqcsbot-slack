"""
Tests for yt.py
"""
from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object

YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v='
# TODO(mitch): work out a way to get this from yt.py without triggering
# 'on_command' to be called and add '!yt' as a handler which messes with
# testing.
NO_QUERY_MESSAGE = "You can't look for nothing. !yt <QUERY>"

def test_yt_no_query(uqcsbot: MockUQCSBot):
    message = generate_message_object(TEST_CHANNEL_ID, "!yt")
    uqcsbot.post_and_handle_command(message)
    channel_messages = uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])
    assert len(channel_messages) == 2
    assert channel_messages[0]['text'] == NO_QUERY_MESSAGE

def test_yt_normal(uqcsbot: MockUQCSBot):
    message = generate_message_object(TEST_CHANNEL_ID, "!yt dog")
    uqcsbot.post_and_handle_command(message)
    channel_messages = uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])
    assert len(channel_messages) == 2
    assert channel_messages[0]['text'][0:len(YOUTUBE_VIDEO_URL)] == YOUTUBE_VIDEO_URL