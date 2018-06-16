from uqcsbot import bot, Command


@bot.on_command("repo")
def handle_repo(command: Command):
    '''
    `!repo` - Returns the url for the uqcsbot repo.
    '''
    bot.post_message(command.channel_id, "https://github.com/UQComputingSociety/uqcsbot")
