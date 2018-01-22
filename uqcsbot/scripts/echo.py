from uqcsbot import bot, Command


@bot.on_command("echo")
def handle_echo(command: Command):
    if command.has_arg():
        bot.post_message(command.channel, command.arg)
