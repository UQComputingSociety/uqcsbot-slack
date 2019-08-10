from uqcsbot import bot
from datetime import datetime
from pytz import timezone, utc
from random import choice


class Pin:
    """
    Class for pins, with channel, age in years, user and pin text
    """
    def __init__(self, channel: str, years: int, user: str, text: str):
        self.channel = channel
        self.years = years
        self.user = user
        self.text = text

    def message(self) -> str:
        return (f"On this day, {self.years} years ago, <@{self.user}> said"
                f"\n>>>{self.text}")

    def origin(self):
        return bot.channels.get(self.channel)


@bot.on_schedule('cron', hour=12, minute=0, timezone='Australia/Brisbane')
def daily_history() -> None:
    """
    Selets a random pin that was posted on this date some years ago,
    and reposts it in the same channel
    """
    anniversary = []
    today = datetime.now(utc).astimezone(timezone('Australia/Brisbane')).date()

    # for every channel
    for channel in bot.api.conversations.list(types="public_channel")['channels']:
        # skip archived channels
        if channel['is_archived']:
            continue

        for pin in bot.api.pins.list(channel=channel['id'])['items']:
            # messily get the date the pin was originally posted
            pin_date = (datetime.fromtimestamp(int(float(pin['message']['ts'])), tz=utc)
                        .astimezone(timezone('Australia/Brisbane')).date())
            # if same date as today
            if pin_date.month == today.month and pin_date.day == today.day:
                # add pin to possibilities
                anniversary.append(Pin(channel=channel['name'], years=today.year-pin_date.year,
                                       user=pin['message']['user'], text=pin['message']['text']))

    # if no pins were posted on this date, do nothing
    if not anniversary:
        return

    # randomly select a pin, and post it in the original channel
    selected = choice(anniversary)
    bot.post_message(selected.origin(), selected.message())
