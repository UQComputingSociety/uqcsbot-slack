from random import random
from uqcsbot import bot, Command

# Maximum number of posts back a user can try to mock
MAX_NUM_POSTS_BACK = 100

def get_nth_most_recent_message(channel_id: str, message_index: int):
    '''
    Given a channel and a message index, will find the message at that index;
    where messages are ordered from most recent to least recent. If the index is
    greater than the number of messages in the channel, will return None.
    '''
    message_count = 0
    # Add 1 to message_index as the 'limit' field is 1-indexed. For example, the
    # 0th message (i.e the first message) can be retrieved by limiting the
    # number of messages to 1.
    message_index += 1
    # As we have set a MAX_NUM_POSTS_BACK upper limit of 100, pagination is not
    # necessary as the first page will contain 100 results by default.
    for page in bot.api.conversations.history(channel=channel_id, limit=message_index):
        messages = page.get('messages', [])
        message_count += len(messages)
        # If we've reached the limit of messages, the final message in this page
        # is the nth most recent message.
        if message_count == message_index:
            return messages[-1]['text']
    return None

def mock_message(message: str):
    '''
    Given a message, will return the mocked version of it. This involves
    randomly varying the case of each letter in the message.

    Example:
      Input: "Mitch, you're acting very immature and should probably stop"
      Output: "MitCh, YoU’RE aCTing vERy ImMatUrE aNd sHOuld pRObAbLy stOp"

    See: http://knowyourmeme.com/memes/mocking-spongebob
    '''
    return ''.join(list(map(lambda l: l.upper() if random() <= 0.5 else l.lower(), message)))

@bot.on_command("mock")
async def handle_mock(command: Command):
    # Add 1 here to account for the calling user's message, which we don't want
    # to mock.
    num_posts_back = int(command.arg) + 1 if command.has_arg() else 1
    if num_posts_back > MAX_NUM_POSTS_BACK:
        bot.post_message(command.channel, f'Cannot recall messages that far back, try under {MAX_NUM_POSTS_BACK}.')
        return

    message_to_mock = get_nth_most_recent_message(command.channel.id, num_posts_back)
    if message_to_mock is None:
        bot.post_message(command.channel, 'No messages exist that far back.')
    else:
        bot.post_message(command.channel, mock_message(message_to_mock))
