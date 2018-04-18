"""
Tests for uqcsbot.scripts.cat
"""
import pytest

from .conftest import MockUQCSBot, TEST_CHANNEL_ID
from .helpers import generate_message_object

@pytest.mark.asyncio
async def test_cat(uqcsbot: MockUQCSBot):
    await uqcsbot.post_and_handle_command(TEST_CHANNEL_ID, '!cat')
    assert len(uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])) == 2
