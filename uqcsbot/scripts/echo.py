from uqcsbot import bot, Command


@bot.on_command("echo")
def handle_echo(command: Command):
    '''
    `!echo [TEXT]` - Echos back the given text.
    '''
    if command.has_arg():
        bot.post_message(command.channel, command.arg)
    else:
        bot.post_message(command.channel, "ECHO!")
