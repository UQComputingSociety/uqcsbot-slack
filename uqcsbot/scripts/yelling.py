from uqcsbot import bot

from string import ascii_lowercase


@bot.on("message")
def yelling(evt: dict):
    """
    Disapproves of people talking quietly in #yelling
    """
    channel = bot.channels.get(evt.get("channel"))

    if channel.name != "yelling":
        return

    if evt.get("subtype") in ["channel_join", "channel_leave"]:
        return

    user = bot.users.get(evt.get("user"))

    if user is None or user.is_bot:
        return

    for c in evt['text']:
        if c in ascii_lowercase:
            bot.api.reactions.add(channel=evt.get("channel"), timestamp=evt['ts'],
                                  name="disapproval")
            return
