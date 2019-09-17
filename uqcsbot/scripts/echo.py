from uqcsbot import bot, Command


@bot.on_command("echo")
def handle_echo(command: Command):
    """
    `!echo [TEXT]` - Echos back the given text.
    """
    bot.post_message(command.channel_id, command.arg if command.has_arg() else 'ECHO!')
