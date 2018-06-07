from random import choice
from uqcsbot import bot, Command

# Maximum number of posts back a user can try to mock
MAX_NUM_POSTS_BACK = 100

def get_nth_most_recent_message(channel_id: str, message_index: int):
    '''
    Given a channel and a message index, will find the message at that index;
    where messages are ordered from most recent to least recent.
    '''
    # Add 1 to message_index as the 'limit' field is 1-indexed. For example, the
    # 0th message (i.e the first message) can be retrieved by limiting the
    # number of messages to 1.
    message_limit = message_index + 1
    # As we have set a MAX_NUM_POSTS_BACK upper limit of 100, pagination is not
    # necessary as the first page will contain 100 results by default.
    history = bot.api.conversations.history(channel=channel_id, limit=message_limit)
    if history['ok'] is not True:
        return None
    messages = history.get('messages', [])
    # Because of the message limit, the final message will be the one we want to
    # mock. If the number of messages does not equal the message limit there was
    # either something wrong with the request or there was not enough
    # conversation history to mock the requested message, so we return None to
    # signify a failure.
    return None if len(messages) != message_limit else messages[-1]['text']

def mock_message(message: str):
    '''
    Given a message, will return the mocked version of it. This involves
    randomly varying the case of each letter in the message.

    Example:
      Input: "Mitch, you're acting very immature and should probably stop"
      Output: "MitCh, YoU’RE aCTing vERy ImMatUrE aNd sHOuld pRObAbLy stOp"

    See: http://knowyourmeme.com/memes/mocking-spongebob
    '''
    return ''.join(choice((c.upper, c.lower))() for c in message)

@bot.on_command("mock")
async def handle_mock(command: Command):
    '''
    `!mock [NUM POSTS]` - Mocks the message from the specified number of
    messages back. If no number is specified, mocks the most recent message.
    '''
    # Add 1 here to account for the calling user's message, which we don't want
    # to mock by default.
    num_posts_back = int(command.arg) + 1 if command.has_arg() else 1
    if num_posts_back > MAX_NUM_POSTS_BACK:
        response = f'Cannot recall messages that far back, try under {MAX_NUM_POSTS_BACK}.'
    elif num_posts_back < 0:
        response = 'Cannot mock into the future (yet)!'
    else:
        message_to_mock = get_nth_most_recent_message(command.channel.id, num_posts_back)
        if message_to_mock is None:
            response = 'Something went wrong (likely insufficient conversation history).'
        else:
            response = mock_message(message_to_mock)
    await bot.as_async.post_message(command.channel, response)
