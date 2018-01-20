from uqcsbot import command_handler, bot
from uqcsbot.command_handler import Command


@command_handler.on("spider")
def handle_spider(command: Command):
    bot.post_message(command.channel, "//\\; ;/\\\\")
