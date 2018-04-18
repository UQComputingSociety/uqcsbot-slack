"""
Tests for uqcsbot.scripts.dog
"""
import pytest

from .conftest import MockUQCSBot, TEST_CHANNEL_ID
from .helpers import generate_message_object

@pytest.mark.asyncio
async def test_dog(uqcsbot: MockUQCSBot):
    await uqcsbot.post_and_handle_command(TEST_CHANNEL_ID, '!dog')
    assert len(uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])) == 2
