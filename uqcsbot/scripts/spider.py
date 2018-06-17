from uqcsbot import bot, Command


@bot.on_command("spider")
def handle_spider(command: Command):
    '''
    `!spider` - Displays the spider shrug.
    '''
    bot.post_message(command.channel_id, "//\\; ;/\\\\")
