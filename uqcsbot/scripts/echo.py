from uqcsbot import command_handler, bot
from uqcsbot.command_handler import Command


@command_handler.on("echo")
def handle_echo(command: Command):
    if command.has_arg():
        bot.post_message(command.channel, command.arg)
