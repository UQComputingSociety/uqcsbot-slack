from uqcsbot import bot, Command
from requests import get
from requests.utils import quote
from bs4 import BeautifulSoup
from typing import List
from functools import partial
import asyncio

ACRONYM_LIMIT = 5
BASE_URL = "http://acronyms.thefreedictionary.com"


async def get_acronyms(loop, word: str) -> (str, List[str]):
    http_response = await loop.run_in_executor(None, partial(get, f"{BASE_URL}/{quote(word)}"))
    html = BeautifulSoup(http_response.content, 'html.parser')
    acronym_tds = html.find_all("td", class_="acr")
    return word, [td.find_next_sibling("td").text for td in acronym_tds]


@bot.on_command("acro")
def handle_acronym(command: Command):
    '''
    `!acro <TEXT>` - Finds an acronym for the given text.
    '''
    if not command.has_arg():
        return

    words = command.arg.split(" ")

    # Requested by @wbo, do not remove unless you get his express permission
    if len(words) == 1:
        word = words[0]
        if word.lower() in [":horse:", "horse"]:
            bot.post_message(command.channel, ">:taco:")
            return
        elif word.lower() in [":rachel:", "rachel"]:
            bot.post_message(command.channel, ">:older_woman:")
            return

    loop = bot.get_event_loop()
    acronym_futures = [get_acronyms(loop, word) for word in words[:ACRONYM_LIMIT]]
    response = ""
    for word, acronyms in loop.run_until_complete(asyncio.gather(*acronym_futures)):
        if acronyms:
            acronym = acronyms[0]
            response += f">{word.upper()}: {acronym}\r\n"
        else:
            response += f"{word.upper()}: No acronyms found!\r\n"

    if len(words) > ACRONYM_LIMIT:
        response += f">I am limited to {ACRONYM_LIMIT} acronyms at once"

    bot.post_message(command.channel, response)
