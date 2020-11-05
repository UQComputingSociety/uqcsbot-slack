from test.conftest import MockUQCSBot
from test.helpers import (generate_event_object, MESSAGE_TYPE_EMOJI_CHANGED,
                          MESSAGE_TYPE_CHANNEL_CREATED)
from unittest.mock import patch


def test_emoji_log(uqcsbot: MockUQCSBot):
    """
    Test !emoji_log for a member adding or removing emoji.
    """
    events = [
        # next event triggers the channel_log function,
        # and so a #uqcs-meta channel needs to exist to post to
        generate_event_object(MESSAGE_TYPE_CHANNEL_CREATED,
                              channel={'id': 'uqcs-meta', 'name': 'uqcs-meta',
                                       'is_public': True}),
        generate_event_object(MESSAGE_TYPE_CHANNEL_CREATED,
                              channel={'id': 'emoji-request', 'name': 'emoji-request',
                                       'is_public': True}),
        # normal add comes with an image URL
        generate_event_object(MESSAGE_TYPE_EMOJI_CHANGED,
                              subtype='add', name='emoji_add_test', value='https://bleh.gif'),
        # alias add comes with the alias name
        generate_event_object(MESSAGE_TYPE_EMOJI_CHANGED,
                              subtype='add', name='alias_add', value='alias:emoji_add_test'),
        generate_event_object(MESSAGE_TYPE_EMOJI_CHANGED,
                              subtype='remove', names=['emoji_remove_test']),
        # if base emoji is removed, aliases go too
        generate_event_object(MESSAGE_TYPE_EMOJI_CHANGED,
                              subtype='remove', names=['emoji_remove_test', 'emoji_remove_alias']),
        # no subtype is valid according to slack API
        generate_event_object(MESSAGE_TYPE_EMOJI_CHANGED, names='emoji_remove_test')
    ]
    with patch('time.sleep') as mock_sleep:
        mock_sleep.return_value = None
        for event in events:
            uqcsbot._run_handlers(event)

    emoji_messages = uqcsbot.test_messages.get('emoji-request', [])
    print(emoji_messages)
    assert len(emoji_messages) == 4
    assert emoji_messages[0]['text'] == 'Emoji added: :emoji_add_test: (`:emoji_add_test:`)'
    assert (emoji_messages[1]['text'] ==
            'Emoji alias added: `:alias_add:` :arrow_right: `:emoji_add_test:` (:alias_add:)')
    assert emoji_messages[2]['text'] == 'Emoji removed: `:emoji_remove_test:`'
    assert (emoji_messages[3]['text'] ==
            'Emojis removed: `:emoji_remove_test:`, `:emoji_remove_alias:`')
