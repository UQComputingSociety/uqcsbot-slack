from uqcsbot import command_handler, bot
from uqcsbot.command_handler import Command


@command_handler.on("cookbook")
def handle_cookbook(command: Command):
    bot.post_message(command.channel, "https://github.com/UQComputingSociety/cookbook")
