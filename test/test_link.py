from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_setting_simple_link(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!link hello world")
    uqcsbot.post_message(TEST_CHANNEL_ID, "!link hello")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert messages[-1]["attachments"][0]["blocks"][0]["text"]["text"] == "hello (global): world"
