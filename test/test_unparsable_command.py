"""
Tests that an unparsable command will result in an exception being thrown.
"""
import pytest

from .conftest import MockUQCSBot, TEST_CHANNEL_ID, UnparsedCommandException
from .helpers import generate_message_object

@pytest.mark.asyncio
async def test_invalid_script_doesnt_match(uqcsbot: MockUQCSBot):
    with pytest.raises(UnparsedCommandException):
        message = generate_message_object(TEST_CHANNEL_ID, None)
        await uqcsbot.post_and_handle_command(message)
