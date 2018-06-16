from uqcsbot import bot, Command
from uqcsbot.util.status_reacts import success_status


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


def get_helper_docs():
    '''
    Returns a sorted list of all the bot's command names and their associated
    helper docstrings. Will filter out any commands that do not have a valid
    helper docstring (see 'is_valid_helper_doc' function above).
    '''
    return sorted((command_name, fn.__doc__)
                  for command_name, functions in bot.command_registry.items()
                  for fn in functions
                  if is_valid_helper_doc(fn.__doc__))


@bot.on_command('help')
@success_status
def handle_help(command: Command):
    """
    `!help [COMMAND]` - Display the helper docstring for the given command. If
    unspecified, will return the helper docstrings for all commands.
    """
    # If a command was specified, only grab its helper docstring. Else, grab all
    # helper docstrings.
    helper_docs = [sanitize_doc(helper_doc)
                   for command_name, helper_doc in get_helper_docs()
                   if not command.has_arg() or command.arg == command_name]
    if len(helper_docs) == 0:
        message = f'Could not find any helper docstrings.'
    else:
        message = '>>>' + '\n'.join(helper_docs)
    user_direct_channel = bot.channels.get(command.user_id)
    bot.post_message(user_direct_channel, message)
