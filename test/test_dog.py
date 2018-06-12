"""
Tests for uqcsbot.scripts.dog
"""
from .conftest import MockUQCSBot
from .helpers import generate_message_object


def test_dog(uqcsbot: MockUQCSBot):
    message = generate_message_object("!dog")
    uqcsbot.test_handle_event(message)
    assert len(uqcsbot.test_posted_messages) == 1
