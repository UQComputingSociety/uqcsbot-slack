from uqcsbot import bot, Command
import asyncio
from random import random

def mock_message(message: str):
    '''
    Given a message, will return the a mocking version of it. This involves
    randomly varying the case of each letter in the message.

    Example:
      Input: "Mitch, you're acting very immature and should probably stop"
      Output: "Mitch, you're acting very immature and should probably stop"

    See: http://knowyourmeme.com/memes/mocking-spongebob
    '''
    return map(lambda l: l.upper() if random() <= 0.5 else l.lower(), message)

@bot.on_command("mock")
async def handle_mock(command: Command):
    # Add one to both to account for the calling user's message
    num_posts_back = command.arg + 1 if command.has_arg() else 1
    *_, message_to_mock = bot.api.conversations.history(limit=num_posts_back).paginate()
    bot.post_message(command.channel, mock_message(message_to_mock))
