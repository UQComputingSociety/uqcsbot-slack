from uqcsbot import bot, Command


@bot.on_command("cookbook")
def handle_cookbook(command: Command):
    bot.post_message(command.channel, "https://github.com/UQComputingSociety/cookbook")
