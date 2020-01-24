from test.conftest import MockUQCSBot, TEST_USER_ID, TEST_DIRECT_ID
from test.helpers import (generate_event_object, MESSAGE_TYPE_CHANNEL_CREATED,
                          MESSAGE_TYPE_MEMBER_JOINED_CHANNEL, MESSAGE_TYPE_TEAM_JOIN)
from unittest.mock import patch

# TODO(mitch): replace this with the milestone number once you've worked out how
# to import files without triggering 'on_command' to be called which messes with testing.
MEMBER_MILESTONE = 50


def test_welcome(uqcsbot: MockUQCSBot):
    """
    Test !welcome for a member joining UQCS.
    """
    events = [
        generate_event_object(MESSAGE_TYPE_CHANNEL_CREATED,
                              channel={'id': 'general', 'name': 'general', 'is_public': True}),
        generate_event_object(MESSAGE_TYPE_CHANNEL_CREATED,
                              channel={'id': 'announcements', 'name': 'announcements',
                                       'is_public': True}),
        generate_event_object(MESSAGE_TYPE_MEMBER_JOINED_CHANNEL,
                              channel='announcements', user=TEST_USER_ID)
    ]
    with patch('time.sleep') as mock_sleep:
        mock_sleep.return_value = None
        for event in events:
            uqcsbot._run_handlers(event)

    general_messages = uqcsbot.test_messages.get('general', [])
    direct_messages = uqcsbot.test_messages.get(TEST_DIRECT_ID, [])
    print(general_messages, direct_messages)
    assert len(direct_messages) > 0
    assert general_messages[-1]['text'] == f'Welcome to UQCS, <@{TEST_USER_ID}>! :tada:'


def test_welcome_milestone(uqcsbot: MockUQCSBot):
    """
    Test !welcome for a member joining on a milestone number.
    """
    events = [generate_event_object(MESSAGE_TYPE_CHANNEL_CREATED,
                                    channel={'id': 'general', 'name': 'general',
                                             'is_public': True}),
              generate_event_object(MESSAGE_TYPE_CHANNEL_CREATED,
                                    channel={'id': 'announcements', 'name': 'announcements',
                                             'is_public': True})]
    for i in range(MEMBER_MILESTONE):
        user_id = 'U' + str(i).rjust(10, '0')
        uqcsbot.test_users[user_id] = {'id': user_id}
        uqcsbot.test_channels[user_id] = {'id': user_id, 'name': user_id}
        events.extend((generate_event_object(MESSAGE_TYPE_CHANNEL_CREATED,
                                             channel={'id': user_id, 'name': user_id}),
                       generate_event_object(MESSAGE_TYPE_TEAM_JOIN, user={'id': user_id}),
                       generate_event_object(MESSAGE_TYPE_MEMBER_JOINED_CHANNEL,
                                             channel='announcements', user=user_id)))
    with patch('time.sleep') as mock_sleep:
        mock_sleep.return_value = None
        for event in events:
            uqcsbot._run_handlers(event)

    general_messages = uqcsbot.test_messages.get('general', [])
    assert len(general_messages) == MEMBER_MILESTONE + 1
    assert general_messages[-1]['text'] == f':tada: {MEMBER_MILESTONE} members! :tada:'
