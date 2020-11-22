from test.conftest import MockUQCSBot
from test.helpers import (generate_event_object, MESSAGE_TYPE_CHANNEL_CREATED)


def test_channel_log(uqcsbot: MockUQCSBot):
    """
    Test channel_log for a member creating a channel
    """
    uqcsbot._run_handlers(generate_event_object(MESSAGE_TYPE_CHANNEL_CREATED,
                                                channel={'id': 'uqcs-meta',
                                                         'name': 'uqcs-meta',
                                                         'is_public': True}))

    message = uqcsbot.test_messages.get('uqcs-meta', [])
    assert len(message) == 1
    assert message[0]['text'] == 'New Channel Created: <#uqcs-meta|uqcs-meta>'
