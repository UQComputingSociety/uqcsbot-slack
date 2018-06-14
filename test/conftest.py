"""
Configuration for Pytest
"""

from unittest.mock import MagicMock
from itertools import islice
from collections import defaultdict, deque
from typing import List, Union, Optional, Callable, DefaultDict, Dict
import pytest
from slackclient import SlackClient

import uqcsbot as uqcsbot_module
from uqcsbot.api import Channel, APIWrapper
from uqcsbot.base import UQCSBot, Command

# Arbitrary channel and user ids for use in testing
TEST_CHANNEL_ID = "C1234567890"
TEST_GROUP_ID = "G1234567890"
TEST_DIRECT_ID = "D1234567890"
TEST_USER_ID = "U1234567890"


class MockUQCSBot(UQCSBot):
    test_posted_messages = None
    test_channels = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_posted_messages = defaultdict(deque)
        self.test_channels = [
            # Public channel
            {'id': TEST_CHANNEL_ID, 'name': TEST_CHANNEL_ID, 'is_public': True},
            # Group channel
            {'id': TEST_GROUP_ID, 'name': TEST_GROUP_ID, 'is_group': True,
             'is_private': True},
            # Direct channel
            {'id': TEST_DIRECT_ID, 'name': TEST_DIRECT_ID, 'is_im': True,
             'is_private': True, 'is_user_deleted': False, 'user': TEST_USER_ID},
        ]

        def mocked_api_call(method, **kwargs):
            '''
            Mocks Slack API call methods.
            '''
            if method == 'channels.list':
                return self.channels_list('channels', **kwargs)
            elif method == 'groups.list':
                return self.channels_list('groups', **kwargs)
            elif method == 'im.list':
                return self.channels_list('ims', **kwargs)
            elif method == 'conversations.members':
                return self.conversations_members(**kwargs)
            elif method == 'conversations.history':
                return self.conversations_history(**kwargs)
            else:
                raise NotImplementedError

        self.mocked_client = MagicMock(spec=SlackClient)
        self.mocked_client.api_call = mocked_api_call
        self._client = self.mocked_client

    @property
    def api(self):
        return APIWrapper(self.mocked_client)

    def conversations_members(self, **kwargs):
        print('trying members')
        channel_id = kwargs.get('channel')
        cursor = kwargs.get('cursor', 0)
        limit = kwargs.get('limit', 100)

        channel = self.channels.get(channel_id)
        if channel is None:
            return {'ok', False}

        all_users = channel.get('users')
        sliced_users = all_users[cursor : cursor + limit + 1]
        cursor += len(sliced_users)
        if cursor == len(all_users):
            cursor = None

        return {'ok': True, 'members': sliced_users, 'cursor': cursor}

    def conversations_history(self, **kwargs):
        print('trying history')
        channel_id = kwargs.get('channel')
        cursor = kwargs.get('cursor', 0)
        limit = kwargs.get('limit', 100)

        all_messages = self.test_posted_messages.get(channel_id, [])
        sliced_messages = list(islice(all_messages, cursor, cursor + limit + 1))
        cursor += len(sliced_messages)
        if cursor == len(all_messages):
            cursor = None

        return {'ok': True, 'messages': sliced_messages, 'cursor': cursor}

    def channels_list(self, channel_type=None, **kwargs):
        print('trying channels')
        cursor = kwargs.get('cursor', 0)
        limit = kwargs.get('limit', 100)

        if channel_type == 'channels':
            filter_function = lambda x: x.get('is_public', False)
        elif channel_type == 'groups':
            filter_function = lambda x: x.get('is_group', False)
        elif channel_type == 'ims':
            filter_function = lambda x: x.get('is_im', False)
        else:
            filter_function = lambda *_: True

        all_channels = list(filter(filter_function, self.test_channels))
        sliced_channels = all_channels[cursor : cursor + limit + 1]
        cursor += len(sliced_channels)
        if cursor == len(all_channels):
            cursor = None

        return {'ok': True, channel_type: sliced_channels, 'cursor': cursor}

    def post_message(self, channel: Union[Channel, str], text: str, **kwargs):
        print(channel)
        channel_id = channel.id if isinstance(channel, Channel) else channel
        print(channel_id)
        message = {'channel_id': channel_id, 'text': text}
        self.test_posted_messages[channel_id].appendleft(message)

    def post_and_handle_command(self, message):
        self.post_message(message['channel'], message['text'])
        command = Command.from_message(message)
        if command.command_name not in self._command_registry:
            raise NotImplementedError()
        for handler in self.command_registry[command.command_name]:
            handler(command)


@pytest.fixture(scope="session")
def _uqcsbot():
    """
    Create a mocked UQCSBot and allow it to find handlers
    Persists for the whole test session
    """
    uqcsbot_module.bot = MockUQCSBot()
    uqcsbot_module.import_scripts()
    return uqcsbot_module.bot


@pytest.fixture()
def uqcsbot(_uqcsbot: MockUQCSBot):
    """
    Clears the `_uqcsbot` fixture before each test
    """
    _uqcsbot.test_posted_messages.clear()
    return _uqcsbot
