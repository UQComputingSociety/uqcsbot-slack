from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from test.helpers import generate_message_object

# TODO(mitch): work out a way to get this from cat.py without triggering
# 'on_command' to be called and add '!cat' as a handler which messes with
# testing.
CAT = "```\n" + \
      "         __..--''``\\--....___   _..,_\n" + \
      "     _.-'    .-/\";  `        ``<._  ``-+'~=.\n" + \
      " _.-' _..--.'_    \\                    `(^) )\n" + \
      "((..-'    (< _     ;_..__               ; `'   fL\n" + \
      "           `-._,_)'      ``--...____..-'\n```"

def test_cat(uqcsbot: MockUQCSBot):
    '''
    test !cat
    '''
    message = generate_message_object(TEST_CHANNEL_ID, '!cat')
    uqcsbot.post_and_handle_command(message)
    channel_messages = uqcsbot.test_posted_messages.get(TEST_CHANNEL_ID, [])
    assert len(channel_messages) == 2
    assert channel_messages[0]['text'] == CAT
