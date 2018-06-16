"""
Tests for uqcsbot.scripts.cat
"""
from .conftest import MockUQCSBot
from .helpers import generate_message_object


def test_latex(uqcsbot: MockUQCSBot):
    message = generate_message_object("!latex test_memes")
    uqcsbot.test_handle_event(message)
    assert len(uqcsbot.test_posted_messages) == 1
    assert uqcsbot.test_posted_messages[-1].text == "LaTeX render for \"test_memes\""