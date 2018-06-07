from uqcsbot import bot, Command
from random import choice

LOADING_REACTS = ['waiting', 'apple_waiting', 'waiting_droid']
SUCCESS_REACTS = ['thumbsup', 'thumbsup_all', 'msn_thumbsup', 'mint', 'nice',
                  'noice', 'feels_good']
HYPE_REACTS = ['nice', 'noice', 'mint', 'exclamation', 'fiestaparrot']

def success_status(command_fn):
    '''
    Decorator function which adds a success react after the wrapped command
    has run. This gives a visual cue to users in the calling channel that
    the wrapped command was carried out successfully.
    '''
    async def wrapper(command: Command):
        success_react = choice(SUCCESS_REACTS)
        reaction_kwargs = {'name': success_react,
                           'channel': command.channel.id,
                           'timestamp': command.message['ts']}
        await command_fn(command)
        await bot.as_async.api.reactions.add(**reaction_kwargs)
    return wrapper

def loading_status(command_fn):
    '''
    Decorator function which adds a loading react before the wrapped command
    has run and removes it once it has successfully completed. This gives a
    visual cue to users in the calling channel that the command is in progress.
    '''
    async def wrapper(command: Command):
        loading_react = choice(LOADING_REACTS)
        reaction_kwargs = {'name': loading_react,
                           'channel': command.channel.id,
                           'timestamp': command.message['ts']}
        await bot.as_async.api.reactions.add(**reaction_kwargs)
        await command_fn(command)
        await bot.as_async.api.reactions.remove(**reaction_kwargs)
    return wrapper
