from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
import pytest
from uqcsbot.utils.command_utils import get_helper_doc

YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v='


def test_yt_no_query(uqcsbot: MockUQCSBot):
    '''
    Test !yt with no query
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, "!yt")
    voteythumbs_doc = get_helper_doc('yt')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == f'usage: {voteythumbs_doc}'


@pytest.mark.skip
def test_yt_normal(uqcsbot: MockUQCSBot):
    '''
    Test !yt with regular query
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, "!yt dog")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'][0:len(YOUTUBE_VIDEO_URL)] == YOUTUBE_VIDEO_URL
