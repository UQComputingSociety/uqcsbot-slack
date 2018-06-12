"""
Tests for yt.py
"""
from test.conftest import MockUQCSBot
from test.helpers import generate_message_object

YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v='
NO_QUERY_MESSAGE = "You can't look for nothing. !yt <QUERY>"

def test_yt_no_query(uqcsbot: MockUQCSBot):
    message = generate_message_object("!yt")
    uqcsbot.test_handle_event(message)
    assert len(uqcsbot.test_posted_messages) == 1
    assert uqcsbot.test_posted_messages[0].text == NO_QUERY_MESSAGE

def test_yt_normal(uqcsbot: MockUQCSBot):
    message = generate_message_object("!yt dog")
    uqcsbot.test_handle_event(message)
    assert len(uqcsbot.test_posted_messages) == 1
    assert uqcsbot.test_posted_messages[0].text[0:len(YOUTUBE_VIDEO_URL)] == YOUTUBE_VIDEO_URL