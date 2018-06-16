from uqcsbot import bot, Command


@bot.on_command("id")
def handle_id(command: Command):
    '''
    `!id` - Returns the calling user's Slack ID.
    '''
    bot.post_message(command.channel_id, f'`{command.user_id}`')
