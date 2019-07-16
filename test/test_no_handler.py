from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
import pytest


def test_not_implemented_command(uqcsbot: MockUQCSBot):
    """
    Tests that the bot correctly detects an invalid command.
    """
    with pytest.raises(NotImplementedError):
        uqcsbot.post_message(TEST_CHANNEL_ID, '!thiscommanddoesntexist')
