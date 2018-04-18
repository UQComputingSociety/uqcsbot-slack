"""
Tests for uqcsbot.scripts.echo
"""
import pytest

from .conftest import MockUQCSBot, TEST_CHANNEL_ID
from .helpers import generate_message_object

@pytest.mark.asyncio
async def test_echo_hello_world(uqcsbot: MockUQCSBot):
    await uqcsbot.post_and_handle_command(TEST_CHANNEL_ID, '!echo Hello, World!')
    channel_messages = uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])
    assert len(channel_messages) == 2
    assert channel_messages[0]['text'] == 'Hello, World!'
