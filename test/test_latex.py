"""
Tests for uqcsbot.scripts.cat
"""
from .conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_latex(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!latex test_memes")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    print(messages)
    assert messages[-1]["text"] == "LaTeX render for \"test_memes\""
    assert len(messages[-1].get("attachments", [])) == 1