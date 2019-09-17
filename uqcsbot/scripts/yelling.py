from uqcsbot import bot

from random import choice, random


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
    if bot.channels.get(channel).name != "yelling":
        return

    # ensure message proper
    if "subtype" in event:
        return

    # ensure user proper
    user = bot.users.get(event.get("user"))
    if user is None or user.is_bot:
        return

    text = event['text']
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
                       f"DID YOU SAY \n>{mutate_minuscule(text)}".upper(),
                       f"WHAT IS THE MEANING OF THIS ARCANE SYMBOL “{random_minuscule(text)}”‽"
                       + " I RECOGNISE IT NOT!"]
                      # the following is a reference to both "The Wicker Man" and "Nethack"
                      + (['OH, NO! NOT THE `a`S! NOT THE `a`S! AAAAAHHHHH!']
                         if 'a' in text else []))

    # check if minuscule in message, and if so, post response
    for c in text:
        if c.islower():
            bot.post_message(channel, response)
            return
