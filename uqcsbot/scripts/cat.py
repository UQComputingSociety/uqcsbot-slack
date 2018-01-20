from uqcsbot import command_handler, bot
from uqcsbot.command_handler import Command


@command_handler.on("cat")
def handle_cat(command: Command):
    cat = "```\n" + \
          "         __..--''``\\--....___   _..,_\n" + \
          "     _.-'    .-/\";  `        ``<._  ``-+'~=.\n" + \
          " _.-' _..--.'_    \\                    `(^) )\n" + \
          "((..-'    (< _     ;_..__               ; `'   fL\n" + \
          "           `-._,_)'      ``--...____..-'\n```"

    bot.post_message(command.channel, cat)
