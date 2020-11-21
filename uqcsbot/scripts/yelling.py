import re
from random import choice, random
from typing import Tuple, Any, List, Optional

from uqcsbot import bot
from uqcsbot.api import User, Channel
from uqcsbot.utils.patterns import URL_PATTERN


def in_yelling(channel: Optional[Channel]) -> bool:
    """
    Checks that channel is #yelling. Exists for test mocking.

    :param channel: the channel the instigating message was sent in
    :return: true if message was sent in yelling, false otherwise
    """
    chan = bot.channels.get(channel)
    return chan and (chan.name == "yelling" or chan.name == "cheering")


def clear_url(message: str) -> Tuple[str, List[Tuple[int, Any]]]:
    """
    Removes any urls in the message and returns the stripped url separately with urls.

    :param message: the instigating message sent to !yelling
    :return: the message with the urls stripped out, list of url starting positions and urls
    """
    # find all urls and their starting positions respectively
    all_urls = [(m.start(0), m.group(0))
                for m in re.finditer(URL_PATTERN, message)]

    return re.sub(URL_PATTERN, '', message).strip(), all_urls


def is_human(user: Optional[User]) -> bool:
    """
    Checks that the user is not a bot. Exists for test mocking.

    :param user: the Slack user who sent the message
    :return: true if user is a human account, false otherwise (e.g. a bot)
    """
    return user is not None and not user.is_bot


def mutate_minuscule(message: str, urls: List[Tuple[int, str]]) -> str:
    """
    Randomly mutates 40% of minuscule letters to other minuscule letters and then inserts the
    original urls to their original places.

    :param message: the instigating message sent to !yelling
    :param urls: a list of pairs of starting indexes and urls to be inserted at those indexes
    :return: the original message modified as described above
    """
    result = ""
    for char in message:
        if char.islower() and random() < 0.4:
            result += choice('abcdefghijklmnopqrstuvwxyz')
        else:
            result += char

    # reinsert all urls into their original positions
    for position, url in urls:
        result = result[:position] + url + result[position:]

    return result


def random_minuscule(message: str) -> str:
    """
    Returns a random minuscule letter from a string.

    :param message: the instigating message sent to !yelling
    :return: one lowercase character from the original message
    """
    possible = ""
    for char in message:
        if char.islower():
            possible += char
    return choice(possible) if possible else ""


@bot.on("message")
def yelling(event: dict) -> None:
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
    text = re.sub(r":[\w\-\+\_']+:", lambda m: m.group(0).upper(), event['text'], flags=re.UNICODE)
    text = text.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")

    # find the url-clean string together with a list of urls and their starting positions
    text, urls = clear_url(text)

    # randomly select a response
    response = choice([
                          "WHAT’S THAT‽",
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
                          f"DID YOU SAY \n>>>{mutate_minuscule(text, urls)}".upper(),
                          f"WHAT IS THE MEANING OF THIS ARCANE SYMBOL “{random_minuscule(text)}”‽"
                          + " I RECOGNISE IT NOT!"]
                      # the following is a reference to both "The Wicker Man" and "Nethack"
                      + (['OH, NO! NOT THE `a`S! NOT THE `a`S! AAAAAHHHHH!']
                         if 'a' in text else []))

    # check if minuscule in message, and if so, post response
    if any(char.islower() for char in text):
        if event.get("subtype") == "thread_broadcast":
            bot.post_message(channel, response, reply_broadcast=True,
                             thread_ts=event.get("thread_ts"))
        else:
            bot.post_message(channel, response, thread_ts=event.get("thread_ts"))
