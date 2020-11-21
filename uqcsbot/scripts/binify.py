from uqcsbot import bot, Command


@bot.on_command("binify")
def handle_binify(command: Command):
    """
    `!binify (binary | ascii)` - Converts a binary string to an ascii string
    or vice versa
    """
    if not command.has_arg():
        response = "Please include string to convert."
    elif set(command.arg).issubset(["0", "1", " "]) and len(command.arg) > 2:
        command.arg = command.arg.replace(" ", "")
        if len(command.arg) % 8 != 0:
            response = "Binary string contains partial byte."
        else:
            response = ""
            for i in range(0, len(command.arg), 8):
                n = int(command.arg[i:i+8], 2)
                if n >= 128:
                    response = "Character out of ascii range (0-127)"
                    break
                response += chr(n)
    else:
        response = ""
        for c in command.arg.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"):
            n = ord(c)
            if n >= 128:
                response = "Character out of ascii range (0-127)"
                break
            response += f"{n:08b}"

    command.reply_with(bot, response)
