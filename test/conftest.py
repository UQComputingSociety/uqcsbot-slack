"""
Configuration for Pytest
"""
import pytest
from typing import List, Union, Optional, Callable

import uqcsbot as uqcsbot_module
from uqcsbot.api import Channel
from uqcsbot.base import UQCSBot, Command


TEST_CHANNEL_ID = u"C2147483705"  # Taken from Slack API docs
TEST_USER_ID = u"U2147483697"  # Taken from Slack API docs


# Bot mocking
class PostedMessage(object):
    def __init__(self, channel_id: str, text: str):
        self.channel_id = channel_id
        self.text = text


class UnparsedCommandException(Exception):
    """
    Unlike the actual bot, an unparsable command will result in this exception rather than being ignored
    Allows the tests to expect this result
    """
    pass


class UnmatchedHandleException(Exception):
    """
    Unlike the actual bot, a message which doesn't match any handlers will raise this exception rather than being ignored
    Allows the tests to expect this result
    """
    pass

class MockUQCSBot(UQCSBot):
    test_posted_messages: List[PostedMessage] = None

    def __init__(self, logger=None):
        super().__init__(logger)
        self.test_posted_messages = []  # A list of posted messages for unit testing
        self.channels = {}  # Allows get to fail. TODO mock channel object

    def test_handle_event(self, message):
        command = Command.from_message(self, message)
        if command is None:
            raise UnparsedCommandException()
        handlers = self._command_registry[command.command_name]
        if not handlers:
            raise UnmatchedHandleException()
        for handler in handlers:
            handler(command)

    def post_message(self, channel: Union[Channel, str], text: str, **kwargs):
        channel_id = channel.id if isinstance(channel, Channel) else channel
        self.test_posted_messages.append(PostedMessage(channel_id, text))


@pytest.fixture(scope="session")
def _uqcsbot():
    """
    Create a mocked UQCSBot and allow it to find handlers
    Persists for the whole test session
    The testing caches are cleared by the `uqcsbot` fixture below
    """
    uqcsbot_module.bot = MockUQCSBot()
    uqcsbot_module.import_scripts()
    return uqcsbot_module.bot


@pytest.fixture()
def uqcsbot(_uqcsbot: MockUQCSBot):
    """
    Clears the `_uqcsbot` fixture before each test
    """
    _uqcsbot.test_posted_messages = []
    return _uqcsbot
