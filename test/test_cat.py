"""
Tests for uqcsbot.scripts.cat
"""
from .conftest import MockUQCSBot
from .helpers import generate_message_object


def test_cat(uqcsbot: MockUQCSBot):
    message = generate_message_object("!cat")
    uqcsbot.test_handle_event(message)
    assert len(uqcsbot.test_posted_messages) == 1
