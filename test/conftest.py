"""
Configuration for Pytest
"""

from itertools import islice
from functools import partial
from collections import defaultdict
import time
from typing import Optional
import pytest
from slack import WebClient
import uqcsbot as uqcsbot_module
from uqcsbot.api import APIWrapper
from uqcsbot.base import UQCSBot, Command
from copy import deepcopy

# Convenient (but arbitrary) channels and users for use in testing
TEST_CHANNEL_ID = "C1234567890"
TEST_GROUP_ID = "G1234567890"
TEST_DIRECT_ID = "D1234567890"
TEST_USER_ID = "U1234567890"
TEST_BOT_ID = "B1234567890"
TEST_USERS = {
    # Bot user
    TEST_BOT_ID: {'id': TEST_BOT_ID, 'name': TEST_BOT_ID, 'deleted': False,
                  'is_bot': True, 'profile': {'display_name': TEST_BOT_ID}},
    # Regular user
    TEST_USER_ID: {'id': TEST_USER_ID, 'name': TEST_USER_ID, 'deleted': False,
                   'profile': {'display_name': TEST_USER_ID}}
}
TEST_CHANNELS = {
    # Public channel
    TEST_CHANNEL_ID: {'id': TEST_CHANNEL_ID, 'name': TEST_CHANNEL_ID,
                      'is_public': True, 'members': [TEST_USER_ID]},
    # Group channel
    TEST_GROUP_ID: {'id': TEST_GROUP_ID, 'name': TEST_GROUP_ID, 'is_group': True,
                    'is_private': True, 'members': [TEST_USER_ID]},
    # Direct channel
    TEST_DIRECT_ID: {'id': TEST_DIRECT_ID, 'name': TEST_DIRECT_ID, 'is_im': True,
                     'is_private': True, 'is_user_deleted': False,
                     'user': TEST_USER_ID}
}
for item in ['is_im', 'is_public', 'is_private', 'is_group']:
    for chan in TEST_CHANNELS.values():
        if item not in chan:
            chan[item] = False


class MockUQCSBot(UQCSBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_messages = defaultdict(list)
        self.test_users = deepcopy(TEST_USERS)
        self.test_channels = deepcopy(TEST_CHANNELS)

        def mocked_api_call(method, *, http_verb='POST', **kwargs):
            '''
            Called the mocked version of a Slack API call.
            '''
            mocked_method = 'mocked_' + method.replace('.', '_')

            if mocked_method not in dir(type(self)):
                raise NotImplementedError(f'{method} has not been mocked.')
            if http_verb == 'GET':
                kwargs.update(kwargs.pop('params', {}))
            elif http_verb == 'POST':
                kwargs.update(kwargs.pop('json', {}))
            return getattr(self, mocked_method)(**kwargs)

        self.mocked_client = WebClient('fake-token')
        self.mocked_client.api_call = mocked_api_call

    @property
    def api(self):
        return APIWrapper(self.mocked_client, self.mocked_client)

    def mocked_users_info(self, **kwargs):
        '''
        Mocks users.info api call.
        '''
        user_id = kwargs.get('user')

        user = self.test_users.get(user_id)
        if user is None:
            return {'ok': False, 'error': 'test'}

        return {'ok': True, 'user': user}

    def mocked_conversations_members(self, **kwargs):
        '''
        Mocks conversations.members api call.
        '''
        channel_id = kwargs.get('channel')
        cursor = kwargs.get('cursor', 0)
        limit = kwargs.get('limit', 100)

        channel = self.test_channels.get(channel_id)
        if channel is None:
            return {'ok': False, 'error': 'test'}

        all_members = channel.get('members', [])
        sliced_members = all_members[cursor: cursor + limit + 1]
        cursor += len(sliced_members)
        if cursor >= len(all_members):
            cursor = None

        return {'ok': True, 'members': sliced_members, 'cursor': cursor}

    def mocked_conversations_history(self, **kwargs):
        '''
        Mocks conversations.history api call.
        '''
        channel_id = kwargs.get('channel')
        cursor = kwargs.get('cursor', 0)
        limit = kwargs.get('limit', 100)

        if channel_id not in self.test_channels:
            return {'ok': False, 'error': 'test'}

        all_messages = self.test_messages.get(channel_id, [])[::-1]  # Most recent first
        sliced_messages = list(islice(all_messages, cursor, cursor + limit + 1))
        cursor += len(sliced_messages)
        if cursor >= len(all_messages):
            cursor = None

        return {'ok': True, 'messages': sliced_messages, 'cursor': cursor}

    def mocked_groups_list(self, **kwargs):
        '''
        Mocks groups.list api call.
        '''
        return self.mocked_channels_list(channel_type='groups', **kwargs)

    def mocked_im_list(self, **kwargs):
        '''
        Mocks im.list api call.
        '''
        return self.mocked_channels_list(channel_type='ims', **kwargs)

    def mocked_conversations_list(self, **kwargs):
        '''
        Mocks conversations.list api call.
        '''
        return self.mocked_channels_list(channel_type='all', **kwargs)

    def mocked_channels_list(self, channel_type='channels', **kwargs):
        '''
        Mocks channels.list api call.
        '''
        cursor = kwargs.get('cursor', 0)
        limit = kwargs.get('limit', 100)

        def is_channel_type(channel, channel_type):
            '''
            Returns whether the given channel is of the given channel type.
            '''
            return channel.get(channel_type, False)

        if channel_type == 'all':
            def filter_function(*args):
                return True
            channel_type = 'channels'  # used later as the response key for the channels
        elif channel_type == 'channels':
            filter_function = partial(is_channel_type, channel_type='is_public')
        elif channel_type == 'groups':
            filter_function = partial(is_channel_type, channel_type='is_group')
        elif channel_type == 'ims':
            filter_function = partial(is_channel_type, channel_type='is_im')
        else:
            return {'ok': False, 'error': 'test'}

        all_channels = list(filter(filter_function, self.test_channels.values()))
        sliced_channels = all_channels[cursor: cursor + limit + 1]
        cursor += len(sliced_channels)
        if cursor >= len(all_channels):
            cursor = None

        return {'ok': True, channel_type: sliced_channels, 'cursor': cursor}

    def mocked_users_list(self, **kwargs):
        '''
        Mocks users.list api call.
        '''
        cursor = kwargs.get('cursor', 0)
        limit = kwargs.get('limit', 100)

        all_members = list(self.test_users.values())
        sliced_members = all_members[cursor: cursor + limit + 1]
        cursor += len(sliced_members)
        if cursor >= len(all_members):
            cursor = None

        return {'ok': True, 'members': sliced_members, 'cursor': cursor}

    def get_channel_message(self, **kwargs) -> Optional[dict]:
        '''
        Convenience function which returns the message at the given channel
        and timestamp.
        '''
        channel_id_or_name = kwargs.get('channel')
        timestamp = kwargs.get('timestamp')

        channel = self.channels.get(channel_id_or_name)
        if channel is None or timestamp is None:
            return None

        channel_messages = self.test_messages.get(channel.id, [])
        # Returns the message with the given timestamp if found, else None.
        return next((m for m in channel_messages if m['ts'] == timestamp), None)

    def mocked_reactions_add(self, **kwargs):
        '''
        Mocks reactions.add api call.
        '''
        name = kwargs.get('name')
        message = self.get_channel_message(**kwargs)
        if name is None or message is None:
            return {'ok': False, 'error': 'test'}
        # Note: 'user' is not a part of Slack API for reactions.add, just a
        # convenient way to set the calling user during testing. If not passed,
        # reaction is assumed to be from bot.
        user = kwargs.get('user', TEST_BOT_ID)

        if 'reactions' not in message:
            message['reactions'] = []

        # Retrieves the reaction with the given name if found, else None.
        reaction_object = next((r for r in message['reactions'] if r['name'] == name), None)
        # If no reaction, add a blank one ready to update.
        if reaction_object is None:
            reaction_object = {'name': name, 'count': 0, 'users': []}
        if user not in reaction_object['users']:
            reaction_object['count'] += 1
            reaction_object['users'].append(user)

        # Removes the reaction from the message so that we can re-add the updated version.
        message['reactions'] = [r for r in message['reactions'] if r['name'] != name]
        message['reactions'].append(reaction_object)
        return {'ok': True}

    def mocked_reactions_remove(self, **kwargs):
        '''
        Mocks reactions.remove api call.
        '''
        name = kwargs.get('name')
        message = self.get_channel_message(**kwargs)
        if name is None or message is None:
            return {'ok': False, 'error': 'test'}
        # Note: 'user' is not a part of Slack API for reactions.add, just a
        # convenient way to set the calling user during testing. If not passed,
        # reaction is assumed to be from bot.
        user = kwargs.get('user', TEST_BOT_ID)

        if 'reactions' not in message:
            return {'ok': False, 'error': 'test'}

        # Retrieves the reaction with the given name if found, else None.
        reaction_object = next((r for r in message['reactions'] if r['name'] == name), None)

        # Error if there was no reaction or the calling user was not a reactee.
        if reaction_object is None:
            return {'ok': False, 'error': 'test'}
        if user not in reaction_object['users']:
            return {'ok': False, 'error': 'test'}

        reaction_object['count'] -= 1
        reaction_object['users'].remove(user)

        # Removes the reaction from the message so that we can re-add the updated version.
        message['reactions'] = [r for r in message['reactions'] if r['name'] != name]
        if reaction_object['count'] > 0:
            message['reactions'].append(reaction_object)
        return {'ok': True}

    def mocked_chat_postMessage(self, **kwargs):
        '''
        Mocks chat.postMessage api call.
        '''
        channel_id_or_name = kwargs.get('channel')
        # Note: 'user' is not a part of Slack API for chat.postMessage, just a
        # convenient way to set the calling user during testing. If not passed,
        # message is assumed to be from bot.
        user = kwargs.get('user', TEST_BOT_ID)

        channel = self.channels.get(channel_id_or_name)
        if channel is None:
            return {'ok': False, 'error': 'test'}

        # Strip the kwargs down to only ones which are valid for this api call.
        # Note: If there is an additional argument you need supported, add it
        # here as well as the intended functionality below.
        stripped_kwargs = {k: v for k, v in kwargs.items()
                           if k in ('text', 'attachments')}
        message = {'type': 'message', 'ts': str(time.time()), 'user': user, **stripped_kwargs}
        # In case we were given a channel name, set channel strictly by the id.
        message['channel'] = channel.id
        self.test_messages[channel.id].append(message)
        self._run_handlers(message)

        return {'ok': True, 'channel': channel.id, 'ts': message['ts'],
                'message': message}

    def _handle_command(self, message: dict) -> None:
        '''
        Handles commands without using an executor.
        '''
        command = Command.from_message(message)
        if command is None:
            return None
        if command.name not in self._command_registry:
            raise NotImplementedError(f'{command.name} is not a registered command.')
        for handler in self._command_registry[command.name]:
            handler(command)
        return None

    def _run_handlers(self, event: dict):
        '''
        Runs handlers without using an executor.
        '''
        handlers = self._handlers[event['type']] + self._handlers['']
        return [handler(event) for handler in handlers]


@pytest.fixture(scope="session")
def _uqcsbot():
    """
    Create a mocked UQCSBot and allow it to find handlers. Persists for the
    whole test session.
    """
    uqcsbot_module.bot = MockUQCSBot()
    uqcsbot_module.import_scripts()
    return uqcsbot_module.bot


@pytest.fixture()
def uqcsbot(_uqcsbot: MockUQCSBot):
    """
    Setup and tear-down steps to run around tests.
    """
    # Anything before yield will be run before test
    # Initialise channels and users
    _uqcsbot.channels._initialise()
    _uqcsbot.users._initialise()
    yield _uqcsbot
    # Anything after yield will be run after test
    # Clear messages, users and channels
    _uqcsbot.test_messages.clear()
    _uqcsbot.test_users = deepcopy(TEST_USERS)
    _uqcsbot.test_channels = deepcopy(TEST_CHANNELS)
