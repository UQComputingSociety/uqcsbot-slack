from uqcsbot import bot, Command


@bot.on_command("cat")
def handle_cat(command: Command):
    """
    `!cat` - Displays the moss cat. Brings torture to CSSE2310 students.
    """
    cat = "\n".join(("```",
                     "         __..--''``\\--....___   _..,_            ",
                     "     _.-'    .-/\";  `        ``<._  ``-+'~=.     ",
                     " _.-' _..--.'_    \\                    `(^) )    ",
                     "((..-'    (< _     ;_..__               ; `'   fL",
                     "           `-._,_)'      ``--...____..-'         ```"))
    bot.post_message(command.channel_id, cat)
