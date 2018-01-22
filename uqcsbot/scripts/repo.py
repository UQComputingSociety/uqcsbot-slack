from uqcsbot import bot, Command


@bot.on_command("repo")
def handle_repo(command: Command):
    bot.post_message(command.channel, "https://github.com/UQComputingSociety/uqcsbot")
