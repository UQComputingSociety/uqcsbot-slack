from uqcsbot import bot

from random import randrange
from re import findall

RESPONSE = ">Multiple exclamation marks are a sure sign of a diseased mind."
MAGIC = 42


def is_human(user):
    """
    checks that the user is not a bot
    exists for test mocking
    """
    return user is not None and not user.is_bot


@bot.on("message")
def exclamation(event: dict):
    """
    Detects and replies to exclamation madness!
    More exclamation marks results in more likely response!!
    One exclamation mark will never produce a response!!!
    Five exclamation marks has a 33% chance of response!!!!
    Nine exclamation marks will guarantee a response!!!!!
    """
    # ensure message proper
    if "subtype" in event and event.get("subtype") != "thread_broadcast":
        return

    # get text
    text = event['text']
    text = text.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
    channel = event.get("channel")

    # count repeated exclamations
    i = 2
    n = 0
    while text.count(i*"!"):
        n += i*len(findall(f'!{{{i},}}', text))
        i += 1

    # semi-randomly respond to multiple
    if randrange(MAGIC) < n:
        if event.get("subtype") == "thread_broadcast":
            bot.post_message(channel, RESPONSE, reply_broadcast=True,
                             thread_ts=event.get("thread_ts"))
        else:
            bot.post_message(channel, RESPONSE, thread_ts=event.get("thread_ts"))
