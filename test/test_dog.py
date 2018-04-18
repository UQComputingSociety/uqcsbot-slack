"""
Tests for uqcsbot.scripts.dog
"""
import pytest

from .conftest import MockUQCSBot, TEST_CHANNEL_ID
from .helpers import generate_message_object

@pytest.mark.asyncio
async def test_dog(uqcsbot: MockUQCSBot):
    message = generate_message_object(TEST_CHANNEL_ID, '!dog')
    await uqcsbot.post_and_handle_command(message)
    assert len(uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])) == 2
