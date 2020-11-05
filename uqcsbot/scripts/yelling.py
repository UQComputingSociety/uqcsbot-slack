from uqcsbot import bot

from random import choice, random
from re import sub, UNICODE


def in_yelling(channel):
    """
    checks that channel is #yelling
    exists for test mocking
    """
    chan = bot.channels.get(channel)
    return chan and (chan.name == "yelling" or chan.name == "cheering")


def mutate_minuscule(message: str) -> str:
    """
    Randomly mutates 40% of minuscule letters to other minuscule letters
    """
    result = ""
    for c in message:
        if c.islower() and random() < 0.4:
            result += choice('abcdefghijklmnopqrstuvwxyz')
        else:
            result += c
    return result


def random_minuscule(message: str) -> str:
    """
    Returns a random minuscule letter from a string
    """
    possible = ""
    for c in message:
        if c.islower():
            possible += c
    return choice(possible) if possible else ""


@bot.on("message")
def yelling(event: dict):
    """
    Responds to people talking quietly in #yelling
    """

    # ensure in #yelling channel
    channel = event.get("channel")
    if not in_yelling(channel):
        return

    # ensure message proper
    if "subtype" in event and event.get("subtype") != "thread_broadcast":
        return

    # ensure user proper
    user = bot.users.get(event.get("user"))
    if user is None or user.is_bot:
        return

    # ignore emoji
    text = sub(r":[\w\-\+\_']+:", lambda m: m.group(0).upper(), event['text'], flags=UNICODE)
    text = text.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
    # randomly select a response
    response = choice(["WHAT’S THAT‽",
                       "SPEAK UP!",
                       "STOP WHISPERING!",
                       "I CAN’T HEAR YOU!",
                       "I THOUGHT I HEARD SOMETHING!",
                       "I CAN’T UNDERSTAND YOU WHEN YOU MUMBLE!",
                       "YOU’RE GONNA NEED TO BE LOUDER!",
                       "WHY ARE YOU SO QUIET‽",
                       "QUIET PEOPLE SHOULD BE DRAGGED OUT INTO THE STREET AND SHOT!",
                       "PLEASE USE YOUR OUTSIDE VOICE!",
                       "IT’S ON THE LEFT OF THE “A” KEY!",
                       "FORMER PRESIDENT THEODORE ROOSEVELT’S FOREIGN POLICY IS A SHAM!",
                       "#YELLING IS FOR EXTERNAL SCREAMING!"
                       + " (FOR INTERNAL SCREAMING, VISIT #CRIPPLINGDEPRESSION!)",
                       ":disapproval:",
                       ":oldmanyellsatcloud:",
                       f"DID YOU SAY \n>>>{mutate_minuscule(text)}".upper(),
                       f"WHAT IS THE MEANING OF THIS ARCANE SYMBOL “{random_minuscule(text)}”‽"
                       + " I RECOGNISE IT NOT!"]
                      # the following is a reference to both "The Wicker Man" and "Nethack"
                      + (['OH, NO! NOT THE `a`S! NOT THE `a`S! AAAAAHHHHH!']
                         if 'a' in text else []))

    # check if minuscule in message, and if so, post response
    if any(c.islower() for c in text):
        if event.get("subtype") == "thread_broadcast":
            bot.post_message(channel, response, reply_broadcast=True,
                             thread_ts=event.get("thread_ts"))
        else:
            bot.post_message(channel, response, thread_ts=event.get("thread_ts"))
