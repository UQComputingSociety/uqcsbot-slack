from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_help_help(uqcsbot: MockUQCSBot):
    """
    Tests `!help help`
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!help help')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == (">>> `!help [COMMAND]` - Display the helper docstring"
                                    + " for the given command. If unspecified, will return"
                                    + " the helper docstrings for all commands. ")
