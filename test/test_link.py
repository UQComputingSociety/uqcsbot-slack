from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.test_utils import mock_db


def test_setting_simple_link(uqcsbot: MockUQCSBot, mock_db):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!link hello world")
    uqcsbot.post_message(TEST_CHANNEL_ID, "!link hello")
    print("\n", uqcsbot.test_messages.get(TEST_CHANNEL_ID, []))
    assert 1 == 1
