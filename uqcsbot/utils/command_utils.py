from random import choice
from functools import wraps
import uqcsbot  # Necessary to avoid circular imports.

LOADING_REACTS = ['waiting', 'apple_waiting', 'waiting_droid']
SUCCESS_REACTS = ['thumbsup', 'thumbsup_all', 'msn_thumbsup', 'ok-hand', 'nice',
                  'noice', 'feels_good']
HYPE_REACTS = ['nice', 'noice', 'ok-hand', 'exclamation', 'fiestaparrot',
               'github_square3', 'sweating']


class UsageSyntaxException(Exception):
    '''
    Raised when a command was used (i.e. called) incorrectly.
    '''
    pass


def sanitize_doc(doc):
    '''
    Returns the doc in sanitized form. This involves removing any newlines and
    whitespace blocks at the start or end of lines.
    '''
    return ' '.join([line.strip() for line in doc.split('\n')])


def is_valid_helper_doc(doc):
    '''
    Returns true if the given docstring is a valid helper docstring. Ignores
    docstrings that have specified they are not a helper docstring by including
    '@no_help' within them.
    '''
    return doc is not None and '@no_help' not in doc


def success_status(command_fn):
    '''
    Decorator function which returns a wrapper function that adds a success
    react after the wrapped command has run. This gives a visual cue to users in
    the calling channel that the command was carried out successfully.
    '''
    @wraps(command_fn)
    def wrapper(command: uqcsbot.Command):
        reaction_kwargs = {'name': choice(SUCCESS_REACTS),
                           'channel': command.channel_id,
                           'timestamp': command.message['ts']}
        res = command_fn(command)
        uqcsbot.bot.api.reactions.add(**reaction_kwargs)
        return res
    return wrapper


def loading_status(command_fn):
    '''
    Decorator function which returns a wrapper function that adds a loading
    react before the wrapped command has run and removes it once it has
    successfully completed. This gives a visual cue to users in the calling
    channel that the command is in progress.
    '''
    @wraps(command_fn)
    def wrapper(command: uqcsbot.Command):
        reaction_kwargs = {'name': choice(LOADING_REACTS),
                           'channel': command.channel_id,
                           'timestamp': command.message['ts']}
        uqcsbot.bot.api.reactions.add(**reaction_kwargs)
        res = command_fn(command)
        uqcsbot.bot.api.reactions.remove(**reaction_kwargs)
        return res
    return wrapper
