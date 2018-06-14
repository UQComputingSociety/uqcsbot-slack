"""
Tests that the bot correctly finds no handlers for an invalid command and ignores it
"""
import pytest

from .conftest import MockUQCSBot, TEST_CHANNEL_ID
from .helpers import generate_message_object

@pytest.mark.asyncio
async def test_invalid_script_doesnt_match(uqcsbot: MockUQCSBot):
    with pytest.raises(NotImplementedError):
        message = generate_message_object(TEST_CHANNEL_ID, '!thiscommanddoesntexist')
        await uqcsbot.post_and_handle_command(message)
