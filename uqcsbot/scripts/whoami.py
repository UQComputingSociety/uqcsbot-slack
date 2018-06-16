from uqcsbot import bot, Command

@bot.on_command("whoami")
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
    bot.post_message(command.channel_id, message)
