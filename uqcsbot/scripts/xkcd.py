import requests
import feedparser
from urllib.parse import quote
from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status


# HTTP Endpoints
XKCD_BASE_URL = "https://xkcd.com/"
XKCD_RSS_URL = "https://xkcd.com/rss.xml"
RELEVANT_XKCD_URL = 'https://relevantxkcd.appspot.com/process?action=xkcd&query='


def get_by_id(comic_number: int) -> str:
    """
    Gets an xkcd comic based on its unique ID/sequence number.
    :param comic_number: the ID number of the xkcd comic to retrieve.
    :return: a response containing either a comic URL or an error message.
    """
    if comic_number < 0:
        return "Invalid xkcd ID, it must be a positive integer."
    url = f"{XKCD_BASE_URL}{str(comic_number)}"
    response = requests.get(url)
    if response.status_code == 200:
        return url
    else:
        return "Could not retrieve an xkcd with that ID (are there even that many?)"


def get_by_search_phrase(phrase: str) -> str:
    """
    Uses the site relevantxkcd.appspot.com to identify the most appropriate xkcd comic
    based on the phrase provided.
    :param phrase: the phrase to find an xkcd comic related to.
    :return: the URL of the most relevant comic for that search phrase.
    """
    url = f"{RELEVANT_XKCD_URL}{quote(phrase)}"
    response = requests.get(url)
    relevant_comics = response.content.decode().split("\n")[2:]
    best_response = relevant_comics[0].split(" ")
    comic_number = int(best_response[0])
    return get_by_id(comic_number)


def get_latest() -> str:
    """
    Gets the most recently published xkcd comic by examining the RSS feed.
    :return: the URL to the latest xkcd comic.
    """
    rss = feedparser.parse(XKCD_RSS_URL)
    latest = rss['entries'][0]['guid']
    return latest


@bot.on_command('xkcd')
@loading_status
def handle_xkcd(command: Command) -> None:
    """
    `!xkcd [COMIC_ID|SEARCH_PHRASE]` - Returns the xkcd comic associated
    with the given COMIC_ID (an integer) or matching the SEARCH_PHRASE.
    Providing no arguments will return the most recent comic.
    """
    if command.has_arg():
        argument = command.arg
        try:
            comic_number = int(argument)
            response = get_by_id(comic_number)
        except ValueError:
            response = get_by_search_phrase(command.arg)
    else:
        response = get_latest()
    bot.post_message(command.channel_id,
                     response,
                     unfurl_links=True,
                     unfurl_media=True)
