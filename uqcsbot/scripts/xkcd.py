import requests
from feedparser import FeedParserDict, parse
from datetime import datetime, timedelta
from urllib.parse import quote
from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status


# HTTP Endpoints
XKCD_BASE_URL = "https://xkcd.com/"
XKCD_RSS_URL = "https://xkcd.com/rss.xml"
RELEVANT_XKCD_URL = 'https://relevantxkcd.appspot.com/process'


def get_by_id(comic_number: int) -> str:
    """
    Gets an xkcd comic based on its unique ID/sequence number.
    :param comic_number: the ID number of the xkcd comic to retrieve.
    :return: a response containing either a comic URL or an error message.
    """
    if comic_number <= 0:
        return "Invalid xkcd ID, it must be a positive integer."
    url = f"{XKCD_BASE_URL}{str(comic_number)}"
    response = requests.get(url)
    if response.status_code != 200:
        return "Could not retrieve an xkcd with that ID (are there even that many?)"
    return url


def get_by_search_phrase(search_phrase: str) -> str:
    """
    Uses the site relevantxkcd.appspot.com to identify the
    most appropriate xkcd comic based on the phrase provided.
    :param search_phrase: the phrase to find an xkcd comic related to.
    :return: the URL of the most relevant comic for that search phrase.
    """
    params = {"action": "xkcd", "query": quote(search_phrase)}
    response = requests.get(RELEVANT_XKCD_URL, params=params)
    # Response consists of a newline delimited list, with two irrelevant first parameters
    relevant_comics = response.content.decode().split("\n")[2:]
    # Each line consists of "comic_id image_url"
    best_response = relevant_comics[0].split(" ")
    comic_number = int(best_response[0])
    return get_by_id(comic_number)


def get_latest() -> FeedParserDict:
    """
    Gets the most recently published xkcd comic by examining the RSS feed.
    :return: the URL to the latest xkcd comic.
    """
    rss = parse(XKCD_RSS_URL)
    latest = rss['entries'][0]
    return latest


def is_id(argument: str) -> bool:
    """
    Determines whether the given argument is a valid id (i.e. an integer).
    :param argument: the string argument to evaluate
    :return: true if the argument can be evaluated as an interger, false otherwise
    """
    try:
        int(argument)
    except ValueError:
        return False
    else:
        return True


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
        if is_id(argument):
            comic_number = int(argument)
            response = get_by_id(comic_number)
        else:
            response = get_by_search_phrase(command.arg)
    else:
        response = get_latest()

    bot.post_message(command.channel_id, response, unfurl_links=True, unfurl_media=True)


@bot.on_schedule('cron', minute=5, day_of_week='mon,wed,fri',
                 timezone='Australia/Brisbane')
def new_xkcd() -> None:
    """
    Posts new xkcd comic when they are released every Monday,
    Wednesday & Friday at 4AM UTC or 2PM Brisbane time.

    @no_help
    """
    latest_xkcd = get_latest()

    published = datetime.strptime(latest_xkcd['published'], "%a, %d %b %Y %H:%M:%S %z")
    now = datetime.utcnow()
    delta = now - published

    if not delta < timedelta(minutes=5):
        return

    day = datetime.today().weekday()

    if day == 0:  # Monday
        message = "Happy Monday, maybe the latest xkcd comic will cheer you up: "
    elif day == 2:  # Wednesday
        message = "Half way through the week, time for the latest xkcd comic: "
    elif day == 4:  # Friday
        message = (":musical_note: It's Friday, Friday\nGotta get down on Friday\n"
                   "Everybody's lookin' forward to the the latest xkcd comic: ")
    else:
        return

    general = bot.channels.get("general")
    bot.post_message(general.id,
                     message + latest_xkcd['guid'],
                     unfurl_links=True,
                     unfurl_media=True)
