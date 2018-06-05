from uqcsbot import bot, Command


@bot.on_command("test")
def handle_test(command: Command):
    for page in bot.api.conversations.members.paginate(limit=1, channel=command.channel.id):
        print(page.get('members'))