from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
from datetime import datetime
from ago import human


@bot.on_command("uptime")
@loading_status
def handle_uptime(command: Command):
    """
    `!uptime` - displays the current uptime for UQCSBot
    """
    t = datetime.now() - bot.starttime
    message = ("The bot has been online for"
               + f" {human(t, precision=(2 if t.total_seconds() >= 60 else 1), past_tense='{}'):s}"
               + (f" (`{round(t.total_seconds()):d}` seconds)" if t.total_seconds() >= 60 else "")
               + f", since {bot.starttime.strftime('%H:%M:%S on %b %d'):s}"
               # adds ordinal suffix
               + f"{(lambda n: 'tsnrhtdd'[(n//10%10!=1)*(n%10<4)*n%10::4])(bot.starttime.day):s}.")
    command.reply_with(bot, message)
