from uqcsbot import command_handler, bot
from uqcsbot.command_handler import Command


@command_handler.on("dog")
def handle_dog(command: Command):
    dog = "```\n" + \
          "                                __\n" + \
          "         ,                    ,\" .\`--o\n" + \
          "        ((                   (  | __,\'\n" + \
          "         \\\\~----------------' \\_;/\n" + \
          "         (                      /\n" + \
          "         /) ._______________.  )\n" + \
          "        (( (               (( (         hjw\n" + \
          "         \`\`-\'               \`\`-\'\n\n```"

    bot.post_message(command.channel, dog)
