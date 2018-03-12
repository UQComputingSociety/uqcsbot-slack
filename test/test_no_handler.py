"""
Tests that the bot correctly finds no handlers for an invalid command and ignores it
"""
import pytest

from .conftest import MockUQCSBot, UnmatchedHandleException
from .helpers import generate_message_object


def test_invalid_script_doesnt_match(uqcsbot: MockUQCSBot):
    message = generate_message_object("!thiscommanddoesntexist")
    with pytest.raises(UnmatchedHandleException):
        uqcsbot.test_handle_event(message)
