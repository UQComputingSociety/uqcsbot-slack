from uqcsbot import bot, Command


@bot.on_command("spider")
def handle_spider(command: Command):
    bot.post_message(command.channel, "//\\; ;/\\\\")
