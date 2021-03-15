from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
from typing import Tuple

import requests
from bs4 import BeautifulSoup

URL = "https://techcrunch.com"

def get_tech_crunch_data(url : str) -> Tuple[int, str]:
    """
    Returns HTML from tech crunch site

    Returns the following tuple: (status code, html text)
    """
    page = requests.get(url)
    return (page.status_code, page.text)

def get_data_from_article(article : str) -> Tuple[str, str]:
    """
    Returns the title of the article and the link

    Tuple returned: (title, url)
    """
    return (article.string.lstrip(), article['href'])

@bot.on_command("news")
@loading_status
def handle_news(command: Command) -> None:
    """
    Handles the web scraping of techcrunch.com when command '!news' is used
    """
    code, data = get_tech_crunch_data(URL)
    if code != 200:
        bot.post_message(command.channel_id, "Could not retrieve data from techcrunch.com :(")
        return

    message = "------------------------- Latest News from TechCrunch ---------------------------\n"
    
    soup = BeautifulSoup(data, "html.parser")
    headlines = soup.find_all("a")
    # Every second <a> tag is the author, therefore this bool is used to skip
    # those
    author = False
    # Used to count the number of headlines that have been reached. For loop
    # break when 5 have been added to the message
    headline = 0
    for article in headlines:
        if article.string != None:
            if not author:
                # Gets headline and link from the article and formats
                # it as a clickable headline
                title, url = get_data_from_article(article)
                message += f"<{url}|{title}>\n\n" 
                headline += 1
            if headline >= 5:
                break
            author = True if not author else False
    bot.post_message(command.channel_id, message, unfurl_links=False, unfurl_media=False)
