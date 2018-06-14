from uqcsbot import bot, Command


@bot.on_command("dog")
def handle_dog(command: Command):
    '''
    `!dog` - Like !cat, but for dog people.
    '''
    dog = "```\n" + \
          "                                __\n" + \
          "         ,                    ,\" .\`--o\n" + \
          "        ((                   (  | __,\'\n" + \
          "         \\\\~----------------' \\_;/\n" + \
          "         (                      /\n" + \
          "         /) ._______________.  )\n" + \
          "        (( (               (( (         hjw\n" + \
          "         \`\`-\'               \`\`-\'\n\n```"

    bot.post_message(command.channel_id, dog)
