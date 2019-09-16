from uqcsbot import bot

from string import ascii_lowercase
from random import choice, random


def mutate_lower(message: str) -> str:
    """
    Randomly mutates 40% of lowercase letters to other letters
    """
    result = ""
    for c in message:
        if c in ascii_lowercase and random() < 0.4:
            result += choice(ascii_lowercase)
        else:
            result += c
    return result


def random_lower(message: str) -> str:
    """
    Gets a random lowercase letter from a string
    """
    possible = ""
    for c in message:
        if c in ascii_lowercase:
            possible += c
    return choice(possible)


@bot.on("message")
def yelling(evt: dict):
    """
    Responds to people talking quietly in #yelling
    """
    channel = bot.channels.get(evt.get("channel"))

    if channel.name != "yelling":
        return

    if evt.get("subtype") in ["channel_join", "channel_leave"]:
        return

    user = bot.users.get(evt.get("user"))

    if user is None or user.is_bot:
        return

    text = evt['text']
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
                       "IT’S NEXT TO THE “A” KEY!",
                       "FORMER PRESIDENT THEODORE ROOSEVELT’S FOREIGN POLICY IS A SHAM!",
                       "#YELLING IS FOR EXTERNAL SCREAMING!"
                       + " (FOR INTERNAL SCREAMING, VISIT #CRIPPLINGDEPRESSION!)",
                       ":disapproval:",
                       ":oldmanyellsatcloud:",
                       f"DID YOU SAY \n>{mutate_lower(text)}".upper(),
                       f"WHAT IS THE MEANING OF THIS ARCANE SYMBOL “{random_lower(text)}”‽"
                       + " I RECOGNISE IT NOT!"])

    for c in text:
        if c in ascii_lowercase:
            bot.post_message(evt.get("channel"), response)
            return
