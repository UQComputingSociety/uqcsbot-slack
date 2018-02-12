from uqcsbot import bot


@bot.on_schedule('cron', hour=17, timezone='Australia/Brisbane')
def wakie():
    print("got event!")
