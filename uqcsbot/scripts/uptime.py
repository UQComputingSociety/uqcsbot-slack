from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
from datetime import datetime
from humanize import precisedelta


@bot.on_command("uptime")
@loading_status
def handle_uptime(command: Command):
    """
    `!uptime` - displays the current uptime for UQCSBot
    """
    t = datetime.now() - bot.start_time
    message = ("The bot has been online for"
               + f" {precisedelta(t, format='%.0f'):s}"
               + (f" (`{round(t.total_seconds()):d}` seconds)" if t.total_seconds() >= 60 else "")
               + f", since {bot.start_time.strftime('%H:%M:%S on %b %d'):s}"
               # adds ordinal suffix
               + f"{(lambda n: 'tsnrhtdd'[(n//10%10!=1)*(n%10<4)*n%10::4])(bot.start_time.day):s}.")
    command.reply_with(bot, message)
