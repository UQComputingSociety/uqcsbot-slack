from test.conftest import MockUQCSBot, TEST_CHANNEL_ID

# TODO(mitch): work out a way to get the cat from cat.py without triggering
# 'on_command' to be called and add '!cat' as a handler which messes with
# testing.


def test_cat(uqcsbot: MockUQCSBot):
    '''
    test !cat
    '''
    uqcsbot.post_message(TEST_CHANNEL_ID, '!cat')
    assert len(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])) == 2
