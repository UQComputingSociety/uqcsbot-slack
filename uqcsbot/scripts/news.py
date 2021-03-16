from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
from typing import Tuple, Dict, List

import feedparser

ARTICLES_TO_POST = 5
URL = "http://feeds.feedburner.com/TechCrunch/"

def get_tech_crunch_data() -> List[Dict[str, str]]:
    """
    Returns data from TechCrunch RSS feed 
    """
    return feedparser.parse(URL).entries

def get_data_from_article(news : List[Dict[str, str]], index : int) -> Tuple[str, str]:
    """
    Returns the title of the article and the link

    Tuple returned: (title, url)
    """
    return (news[index]['title'], news[index]['link'])    

@bot.on_command("news")
@loading_status
def handle_news(command: Command) -> None:
    """
    Prints the 5 top-most articles in the Latest News Section of TechCrunch
    using RSS feed
    """
    message = "------------------------- Latest News from TechCrunch ---------------------------\n"
    news = get_tech_crunch_data()
    for i in range(ARTICLES_TO_POST):
        title, url = get_data_from_article(news, i)
        message += f"<{url}|{title}>\n\n"
    bot.post_message(command.channel_id, message, unfurl_links=False, unfurl_media=False)
