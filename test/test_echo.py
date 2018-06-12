"""
Tests for uqcsbot.scripts.echo
"""
from .conftest import MockUQCSBot
from .helpers import generate_message_object


def test_echo_hello_world(uqcsbot: MockUQCSBot):
    message = generate_message_object("!echo Hello, World!")
    uqcsbot.test_handle_event(message)
    assert uqcsbot.test_posted_messages[0].text == "Hello, World!"
