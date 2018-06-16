from uqcsbot import bot, Command
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

NO_QUERY_MESSAGE = "You can't look for nothing. `!umart <QUERY>`"
NO_RESULTS_MESSAGE = "I can't find anything. Try `!umart <SOMETHING NOT AS SPECIFIC>`"
ERROR_MESSAGE = "I tried to get the things but alas I could not. Error with HTTP Request."

UMART_SEARCH_URL = "https://www.umart.com.au/umart1/pro/products_list_searchnew_min.phtml"
UMART_PRODUCT_URL = "https://www.umart.com.au/umart1/pro/"


@bot.on_command("umart")
def handle_umart(command: Command):
    """
    `!umart <QUERY>` - Returns up to 5 top results for products from umart matching the search query.
    """
    # Makes sure the query is not empty
    if not command.has_arg():
        bot.post_message(command.channel, NO_QUERY_MESSAGE)
        return
    search_query = command.arg.strip()
    # Detects if user is being smart
    if "SOMETHING NOT AS SPECIFIC" in search_query:
        bot.post_message(command.channel, "Not literally...")
        return
    search_results = get_umart_results(search_query)
    if not search_results:
        bot.post_message(command.channel, ERROR_MESSAGE)
        return
    if len(search_results) == 0:
        bot.post_message(command.channel, NO_RESULTS_MESSAGE)
        return
    message = "```"
    for result in search_results:
        message += f"Name: <{UMART_PRODUCT_URL}{result['link']}|{result['name']}>\n"
        message += f"Price: {result['price']}\n"
    message += "```"
    bot.post_message(command.channel, message)


def get_umart_results(search_query):
    """
    Gets the top results based on the search_query.
    Returns up to 5 results.
    """
    search_page = get_search_page(search_query)
    if search_page is None:
        return None
    search_results = get_results_from_page(search_page)
    return search_results


def get_results_from_page(search_page):
    """
    Strips results from html page
    """
    html = BeautifulSoup(search_page, "html.parser")
    search_items = []
    for li in html.select("li"):
        name = li.select("a.proname")[0].get_text()
        price = li.select("dl:nth-of-type(2) > dd > span")[0].get_text()
        link = li.select("a.proname")[0]["href"]
        search_items.append({"name": name, "price": price, "link": link})
    return search_items


def get_search_page(search_query):
    """
    Gets the search page HTML
    """
    try:
        with closing(get(UMART_SEARCH_URL+"?search="+search_query+"&bid=2")) as resp:
            return resp.content
    except RequestException as e:
        bot.logger.error(
            f"A request error {e.resp.status} occurred:\n{e.content}")
        return None
