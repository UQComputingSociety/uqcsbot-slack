from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from uqcsbot.utils.command_utils import get_helper_doc


def test_voteythumbs(uqcsbot: MockUQCSBot):
    '''
    Tests !voteythumbs
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, '!voteythumbs ye/na/maybz?')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    # Make sure there are three reactions (thumbsup, thumbsdown, eyes)
    assert len(messages[-1]['reactions']) == 3
