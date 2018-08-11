from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import success_status


@bot.on_command("whoami")
@success_status
def handle_whoami(command: Command):
    '''
    `!whoami` - Returns the Slack information for the calling user.
    '''
    response = bot.api.users.info(user=command.user_id)
    if not response['ok']:
        message = 'An error occurred, please try again.'
    else:
        user_info = response['user']
        message = f'```{user_info}```'
    user_direct_channel = bot.channels.get(command.user_id)
    bot.post_message(user_direct_channel, message)
