"""
Tests for yt.py
"""
from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch
import pytest
import random
import string

YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v="
# TODO(mitch): work out a way to get this from yt.py without triggering
# 'on_command' to be called and add '!yt' as a handler which messes with
# testing.
NO_QUERY_MESSAGE = "You can't look for nothing. !yt <QUERY>"

def mocked_search_execute(search_query: str, search_part: str, search_type: str, max_results: int):
    """
    Currently only returns a response of video ID's based on max_results.
    Otherwise returns none.
    """
    if search_type == 'video' and search_part == 'id':
        items = []
        for _ in range(max_results):
            # The following line generates an 11 character random string of ascii and digits
            # This simulates a videoId returned by the google api client
            videoId = ''.join(random.choices(
                string.ascii_letters + string.digits, k=11))
            # The response from the client contains a list of items
            # Each item has id object containing a string called videoId
            items.append({'id': {'videoId': videoId}})
        return {'items': items}
    return None

def test_yt_no_query(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!yt")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == NO_QUERY_MESSAGE

@patch("uqcsbot.scripts.yt.execute_search", new=mocked_search_execute)
def test_yt_normal(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!yt dog")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    print(messages)
    assert len(messages) == 2
    assert messages[-1]['text'][0:len(YOUTUBE_VIDEO_URL)] == YOUTUBE_VIDEO_URL
