from uqcsbot import bot, Command
from random import choice

# TODO(mitch): add other success emojis
SUCCESS_REACTS = ['thumbsup']

def success_status(fn):
    '''
    Decorator function which adds a success react after the wrapped function
    has run. This gives a visual cue to users in the calling channel that
    the wrapped function was carried out successfully.
    '''
    async def wrapper(command: Command):
        loading_react = choice(SUCCESS_REACTS)
        reaction_kwargs = {'name': loading_react,
                           'channel': command.channel.id,
                           'timestamp': command.message['ts']}
        await fn(command)
        await bot.as_async.api.reactions.add(**reaction_kwargs)
    return wrapper
