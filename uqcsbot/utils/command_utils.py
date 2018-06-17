import uqcsbot  # "import all" required to avoid circular imports
from functools import wraps
from random import choice

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


def usage_helper(command_fn):
    '''
    Decorator function which detects whether the command was called correctly
    and returns the correct usage helper doc if not.
    '''
    @wraps(command_fn)
    def wrapper(command: uqcsbot.Command):
        try:
            command_fn(command)
        except UsageSyntaxException as e:
            helper_doc = sanitize_doc(command_fn.__doc__)
            uqcsbot.bot.post_message(command.channel_id, f'usage: {helper_doc}')
    return wrapper


def success_status(command_fn):
    '''
    Decorator function which adds a success react after the wrapped command
    has run. This gives a visual cue to users in the calling channel that
    the wrapped command was carried out successfully.
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
    Decorator function which adds a loading react before the wrapped command
    has run and removes it once it has successfully completed. This gives a
    visual cue to users in the calling channel that the command is in progress.
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
