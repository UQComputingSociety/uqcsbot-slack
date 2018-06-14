"""
Configuration for Pytest
"""

from unittest.mock import MagicMock
from itertools import islice
from collections import defaultdict, deque
from typing import List, Union, Optional, Callable, DefaultDict, Dict
import pytest
import time
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
    test_channels = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_channels = {
            # Public channel
            TEST_CHANNEL_ID: {'id': TEST_CHANNEL_ID, 'name': TEST_CHANNEL_ID,
                              'is_public': True, 'members': [TEST_USER_ID],
                              'messages': []},
            # Group channel
            TEST_GROUP_ID: {'id': TEST_GROUP_ID, 'name': TEST_GROUP_ID,
                            'is_group': True, 'is_private': True,
                            'members': [TEST_USER_ID], 'messages': []},
            # Direct channel
            TEST_DIRECT_ID: {'id': TEST_DIRECT_ID, 'name': TEST_DIRECT_ID,
                             'is_im': True, 'is_private': True,
                             'is_user_deleted': False, 'user': TEST_USER_ID,
                             'messages': []}
        }

        def mocked_api_call(method, **kwargs):
            '''
            Mocks Slack API call methods.
            '''
            if method == 'channels.list':
                return self.mocked_channels_list('channels', **kwargs)
            elif method == 'groups.list':
                return self.mocked_channels_list('groups', **kwargs)
            elif method == 'im.list':
                return self.mocked_channels_list('ims', **kwargs)
            elif method == 'conversations.members':
                return self.mocked_conversations_members(**kwargs)
            elif method == 'conversations.history':
                return self.mocked_conversations_history(**kwargs)
            elif method == 'chat.postMessage':
                return self.mocked_chat_post_message(**kwargs)
            else:
                raise NotImplementedError

        self.mocked_client = MagicMock(spec=SlackClient)
        self.mocked_client.api_call = mocked_api_call

    @property
    def api(self):
        return APIWrapper(self.mocked_client)

    def mocked_conversations_members(self, **kwargs):
        channel_id = kwargs.get('channel')
        cursor = kwargs.get('cursor', 0)
        limit = kwargs.get('limit', 100)

        channel = self.test_channels.get(channel_id)
        if channel is None:
            return {'ok': False}

        all_users = channel.get('members', [])
        sliced_users = all_users[cursor : cursor + limit + 1]
        cursor += len(sliced_users)
        if cursor == len(all_users):
            cursor = None

        return {'ok': True, 'members': sliced_users, 'cursor': cursor}

    def mocked_conversations_history(self, **kwargs):
        channel_id = kwargs.get('channel')
        cursor = kwargs.get('cursor', 0)
        limit = kwargs.get('limit', 100)

        channel = self.test_channels.get(channel_id)
        if channel is None:
            return {'ok': False}

        all_messages = channel.get('messages', [])
        ordered_messages = all_messages[::-1] # Most recent first
        sliced_messages = list(islice(ordered_messages, cursor, cursor + limit + 1))
        cursor += len(sliced_messages)
        if cursor == len(all_messages):
            cursor = None

        return {'ok': True, 'messages': sliced_messages, 'cursor': cursor}

    def mocked_channels_list(self, channel_type=None, **kwargs):
        cursor = kwargs.get('cursor', 0)
        limit = kwargs.get('limit', 100)

        if channel_type == 'channels':
            filter_function = lambda x: x.get('is_public', False)
        elif channel_type == 'groups':
            filter_function = lambda x: x.get('is_group', False)
        elif channel_type == 'ims':
            filter_function = lambda x: x.get('is_im', False)
        else:
            return {'ok': False}

        all_channels = list(filter(filter_function, self.test_channels.values()))
        sliced_channels = all_channels[cursor : cursor + limit + 1]
        cursor += len(sliced_channels)
        if cursor == len(all_channels):
            cursor = None

        return {'ok': True, channel_type: sliced_channels, 'cursor': cursor}

    def mocked_chat_post_message(self, **kwargs):
        channel_id_or_name = kwargs.get('channel')
        text = kwargs.get('text')

        channel = self.channels.get(channel_id_or_name)
        if channel is None:
            return {'ok': False}

        message = {'text': text}
        self.test_channels.get(channel.id, {}).get('messages', []).append(message)

        return {'ok': True, 'channel': channel.id, 'ts': str(time.time()),
                'message': message}

    def post_and_handle_message(self, message):
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
    # Clear channel messages
    for channel in _uqcsbot.test_channels.values():
        channel['messages'] = []
    return _uqcsbot
