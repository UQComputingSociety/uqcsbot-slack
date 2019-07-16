from test.conftest import MockUQCSBot, TEST_CHANNEL_ID

# TODO(mitch): work out a way to get the dog from dog.py without triggering
# 'on_command' to be called and add '!dog' as a handler which messes with testing.


def test_dog(uqcsbot: MockUQCSBot):
    """
    test !dog
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!dog')
    assert len(uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])) == 2
