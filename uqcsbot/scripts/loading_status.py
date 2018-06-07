from uqcsbot import bot, Command
from random import choice

LOADING_REACTS = ['waiting', 'apple_waiting', 'waiting_droid', 'keen', 'fiestaparrot']

def loading_status(fn):
    '''
    Decorator function which adds a loading react before the wrapped function
    has run and removes it once it has successfully completed. This gives a
    visual cue to users in the calling channel that the function is in progress.
    '''
    async def wrapper(command: Command):
        loading_react = choice(LOADING_REACTS)
        reaction_kwargs = {'name': loading_react,
                           'channel': command.channel.id,
                           'timestamp': command.message['ts']}
        await bot.as_async.api.reactions.add(**reaction_kwargs)
        await fn(command)
        await bot.as_async.api.reactions.remove(**reaction_kwargs)
    return wrapper
