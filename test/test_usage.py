from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from uqcsbot.utils.command_utils import get_helper_docs


def test_usage(uqcsbot: MockUQCSBot):
    '''
    Tests that the bot correctly handles an incorrectly used command.
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, '!voteythumbs')
    voteythumbs_doc = get_helper_docs('voteythumbs')[0]
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == f'usage: {voteythumbs_doc}'
