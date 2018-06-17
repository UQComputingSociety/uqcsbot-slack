"""
Tests for yt.py
"""
from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
import pytest

YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v='


@pytest.mark.skip
def test_yt_normal(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!yt dog")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'][0:len(YOUTUBE_VIDEO_URL)] == YOUTUBE_VIDEO_URL
