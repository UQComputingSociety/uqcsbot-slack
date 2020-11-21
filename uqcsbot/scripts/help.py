from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import success_status, get_helper_docs


@bot.on_command('help')
@success_status
def handle_help(command: Command):
    """
    `!help [COMMAND]` - Display the helper docstring for the given command.
    If unspecified, will return the helper docstrings for all commands.
    """

    # get helper docs
    helper_docs = get_helper_docs(command.arg)
    if len(helper_docs) == 0:
        message = 'Could not find any helper docstrings.'
    else:
        message = '>>>' + '\n'.join(helper_docs)

    # post helper docs
    if command.arg:
        command.reply_with(bot, message)
    else:
        bot.post_message(command.user_id, message, as_user=True)
