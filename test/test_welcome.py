from test.conftest import MockUQCSBot, TEST_CHANNEL_ID, TEST_USER_ID, TEST_DIRECT_ID
from test.helpers import (generate_event_object, MESSAGE_TYPE_CHANNEL_CREATED,
                          MESSAGE_TYPE_MEMBER_JOINED_CHANNEL)
from unittest.mock import patch

def test_welcome(uqcsbot: MockUQCSBot):
    '''
    Test !welcome for a member joining UQCS.
    '''
    events = [
        generate_event_object(MESSAGE_TYPE_CHANNEL_CREATED,
                              channel={'id': 'general', 'name': 'general',
                                       'is_public': True}),
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
    assert general_messages[-1]['text'] == f'Welcome, {TEST_USER_ID}!'

def test_welcome_milestone(uqcsbot: MockUQCSBot):
    '''
    Test !welcome for a member joining on a milestone number.
    '''
    # TODO(mitch): replace this with the milestone number once you've worked out
    # how to import files without triggering 'on_command' to be called which
    # messes with testing.
    NUM_JOINED_MEMBERS = 50
    events = [
        generate_event_object(MESSAGE_TYPE_CHANNEL_CREATED,
                              channel={'id': 'general', 'name': 'general',
                                       'is_public': True}),
        generate_event_object(MESSAGE_TYPE_CHANNEL_CREATED,
                              channel={'id': 'announcements', 'name': 'announcements',
                                       'is_public': True}),
    ]
    for i in range(NUM_JOINED_MEMBERS):
        events.append(
            generate_event_object(MESSAGE_TYPE_MEMBER_JOINED_CHANNEL,
                                  channel='announcements', user=TEST_USER_ID)
        )
    with patch('time.sleep') as mock_sleep:
        mock_sleep.return_value = None
        for event in events:
            uqcsbot._run_handlers(event)

    general_messages = uqcsbot.test_messages.get('general', [])
    assert len(general_messages) == NUM_JOINED_MEMBERS + 1
    assert general_messages[-1]['text'] == f':tada: {NUM_JOINED_MEMBERS} members! :tada:'
