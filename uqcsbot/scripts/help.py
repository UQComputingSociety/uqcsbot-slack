from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import success_status, get_helper_docs


@bot.on_command('help')
@success_status
def handle_help(command: Command):
    """
    `!help [COMMAND]` - Display the helper docstring for the given command. If
    unspecified, will return the helper docstrings for all commands.
    """
    helper_docs = get_helper_docs(command.arg)
    if len(helper_docs) == 0:
        message = f'Could not find any helper docstrings.'
    else:
        message = '>>>' + '\n'.join(helper_docs)
    user_direct_channel = bot.channels.get(command.user_id)
    bot.post_message(user_direct_channel, message)
