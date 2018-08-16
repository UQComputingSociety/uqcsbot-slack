from uqcsbot import bot, Command


@bot.on_command("conduct")
def handle_conduct(command: Command):
    '''
    `!conduct` - Returns the url for the uqcs code of conduct.
    '''
    bot.post_message(command.channel_id, "https://github.com/UQComputingSociety/code-of-conduct")
