from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object
import pytest

def test_not_implemented_command(uqcsbot: MockUQCSBot):
    '''
    Tests that the bot correctly detects an invalid command.
    '''
    with pytest.raises(NotImplementedError):
        message = generate_message_object(TEST_CHANNEL_ID, '!thiscommanddoesntexist')
        uqcsbot.post_and_handle_message(message)
