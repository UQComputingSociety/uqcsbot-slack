"""
Tests for uqcsbot.scripts.mock
"""
import pytest

from .conftest import MockUQCSBot, TEST_CHANNEL_ID
from .helpers import generate_message_object

@pytest.mark.asyncio
async def test_mock(uqcsbot: MockUQCSBot):
    message = 'I\'m going to say a really long sentence that has a really low' \
              + ' probability of outputting a random-case mocked message that' \
              + ' is equal to the original.'
    uqcsbot.post_message(TEST_CHANNEL_ID, message)
    mock_call = generate_message_object(TEST_CHANNEL_ID, '!mock')
    await uqcsbot.post_and_handle_command(mock_call)
    channel_messages = uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])
    assert len(channel_messages) == 3
    assert channel_messages[0]['text'].lower() == message.lower()
    assert channel_messages[0]['text'] != message
