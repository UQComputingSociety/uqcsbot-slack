from uqcsbot import bot, Command
from time import time, localtime, strftime


@bot.on_command("uptime")
def handle_uptime(command: Command):
    """
    `!uptime` - displays the current uptime for UQCSBot
    """
    t = round(time() - bot.starttime)
    s = t % 60
    m = (t//60) % 60
    h = (t//3600) % 24
    d = (t//86400)
    message = (f"`{t:d}`\n" +
               (f"{d:d}d " if d else "")
               + (f"{h:d}h " if d or h else "")
               + (f"{m:d}m " if d or h or m else "")
               + (f"{s:d}s " if d or h or m or s else "") + "\n" +
               strftime("%H:%M:%S - %b %d", localtime(bot.starttime)))
    command.reply_with(bot, message)
