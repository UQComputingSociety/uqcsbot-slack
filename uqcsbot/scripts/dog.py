from uqcsbot import bot, Command


@bot.on_command("dog")
def handle_dog(command: Command):
    """
    `!dog` - Like !cat, but for dog people.
    """
    dog = "\n".join(("```",
                     "                          _         ",
                     "                       ,:'/   _..._ ",
                     "                      // ( `""-.._.'",
                     "                      \\| /    O\\___",
                     "                      |    O       4",
                     "                      |            /",
                     "                      \\_       .--' ",
                     "                      (_'---'`)     ",
                     "                      / `'---`()    ",
                     "                    ,'        |     ",
                     "    ,            .'`          |     ",
                     "    )\\       _.-'             ;     ",
                     "   / |    .'`   _            /      ",
                     " /` /   .'       '.        , |      ",
                     "/  /   /           \\   ;   | |      ",
                     "|  \\  |            |  .|   | |      ",
                     " \\  `\"|           /.-' |   | |      ",
                     "  '-..-\\       _.;.._  |   |.;-.    ",
                     "        \\    <`.._  )) |  .;-. ))   ",
                     "        (__.  `  ))-'  \\_    ))'    ",
                     "            `'--\"`  jgs  `\"\"\"`      ```"))

    bot.post_message(command.channel_id, dog)
