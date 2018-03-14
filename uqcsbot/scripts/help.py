from uqcsbot import bot, Command
from functools import partial

def sanitize_doc(doc):
    '''
    Returns the doc in sanitized form. This involves removing any newlines and
    whitespace blocks at the start or end of lines.
    '''
    return ' '.join([line.strip() for line in doc.split('\n')])

def is_valid_doc(doc):
    '''
    Returns true if a doc was found and it was not the doc for partial, else
    returns false.

    The check for `partial` doc equality is necessary as some commands are
    declared as async, which gets wrapped in a `partial` by uqcsbot. If the
    async commands possess no docstring of their own, they will by default adopt
    the `partial` docstring instead of None (which is the case for non-async
    commands with no docstring).
    '''
    return doc != None and doc != partial.__doc__

def get_helper_docs():
    '''
    Returns a generator of all the bot's command names and their associated
    helper docstrings. Will filter out any commands that do not have valid
    docstrings (see: is_valid_doc).
    '''
    return ((command_name, fn.__doc__)
            for command_name, functions in bot.command_registry.items()
            for fn in functions
            if is_valid_doc(fn.__doc__))

@bot.on_command('help')
async def handle_help(command: Command):
    """
    TODO(mcdermottm): write this command docstring, and every other docstring
    """
    helper_docs = [sanitize_doc(helper_doc)
                   for command_name, helper_doc in get_helper_docs()
                   if not command.has_arg() or command.arg == command_name]

    user_direct_channel = bot.channels.get(command.user_id, None)
    if len(helper_docs) == 0:
        bot.post_message(user_direct_channel, f'Could not find any helper docstrings.')
    else:
        bot.post_message(user_direct_channel, '>>>' + '\n'.join(helper_docs))
