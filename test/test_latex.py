from .conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_latex(uqcsbot: MockUQCSBot):
    """
    Tests that !latex returns a message with correct text and 1 attachment.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!latex test_memes")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]["text"] == "LaTeX render for \"test_memes\""
    assert len(messages[-1].get("attachments", [])) == 1
