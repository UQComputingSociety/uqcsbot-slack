from uqcsbot import command_handler, bot
from uqcsbot.command_handler import Command


@command_handler.on("repo")
def handle_repo(command: Command):
    bot.post_message(command.channel, "https://github.com/UQComputingSociety/uqcsbot")
