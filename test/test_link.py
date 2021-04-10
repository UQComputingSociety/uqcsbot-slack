from test.conftest import MockUQCSBot, TEST_CHANNEL_ID, TEST_GROUP_ID


def get_last_slackblocks_message_text(messages) -> str:
    """
    Utility methods for retrieving the text content of the most recent message.
    Assumes that message was constructed using a single SlackBlocks SectionBlock with
    at least one attachment.
    :raises KeyError: likely because the last messages was not a SlackBlocks message
    :raises IndexError: if there are no messages in `messages`
    """
    return messages[-1]["attachments"][0]["blocks"][0]["text"]["text"]


class TestLink:
    def test_incorrect_usage_generates_usage_instructions(self, uqcsbot: MockUQCSBot):
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link")
        messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
        assert messages[-1]["attachments"][0]["color"] == "#ffff00"
        assert get_last_slackblocks_message_text(messages) \
               == """usage: !link [-c | -g] [-f] key [value [value ...]]

positional arguments:
  key                   Lookup key
  value                 Value to associate with key

optional arguments:
  -c, --channel         Ensure a channel link is retrieved, or none is
  -g, --global          Ignore channel link and force retrieval of global
  -f, --force-override  Must be passed if overriding a link
"""

    def test_can_set_and_retrieve_basic_global_link(self, uqcsbot: MockUQCSBot):
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link hello world")
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link hello")
        messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
        assert get_last_slackblocks_message_text(messages) \
               == "hello (global): world"

    def test_channel_link_not_available_outside_channel(self, uqcsbot: MockUQCSBot):
        uqcsbot.post_message(TEST_GROUP_ID, "!link -c jobs jobs.uqcs.org")
        uqcsbot.post_message(TEST_GROUP_ID, "!link jobs")
        messages = uqcsbot.test_messages.get(TEST_GROUP_ID, [])
        assert get_last_slackblocks_message_text(messages) \
               == f"jobs ({TEST_GROUP_ID}): jobs.uqcs.org"
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link jobs")
        messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
        assert get_last_slackblocks_message_text(messages) \
               == "No link found for key: `jobs`"

    def test_channel_links_are_returned_by_default(self, uqcsbot: MockUQCSBot):
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link rob schneider")
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link -c rob thomas")
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link rob")
        messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
        assert get_last_slackblocks_message_text(messages) \
               == f"rob ({TEST_CHANNEL_ID}): thomas"

    def test_flag_must_be_passed_to_overwrite(self, uqcsbot: MockUQCSBot):
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link tyler durden")
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link tyler the creator")
        messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
        assert messages[-1]["text"] == "Link already exists, use `-f` to override:"
        assert get_last_slackblocks_message_text(messages) \
               == f"tyler (global): durden"
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link -f tyler the creator")
        messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
        assert messages[-1]["text"] == "Successfully overrode link:"
        assert get_last_slackblocks_message_text(messages) \
               == f"tyler (global): the creator"
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link tyler")
        messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
        assert get_last_slackblocks_message_text(messages) \
               == f"tyler (global): the creator"

    def test_forcing_channel_wont_find_global_links(self, uqcsbot: MockUQCSBot):
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link keanu reeves")
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link -c keanu")
        messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
        assert get_last_slackblocks_message_text(messages) \
               == f"No link found for key: `keanu` in channel `{TEST_CHANNEL_ID}`"

    def test_forcing_global_wont_find_channel_links(self, uqcsbot: MockUQCSBot):
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link bobby tables")
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link -c bobby tarantino")
        uqcsbot.post_message(TEST_CHANNEL_ID, "!link -g bobby")
        messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
        assert get_last_slackblocks_message_text(messages) \
               == f"bobby (global): tables"
