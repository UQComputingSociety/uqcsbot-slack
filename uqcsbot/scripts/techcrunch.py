from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
from typing import Tuple, Dict, List

import feedparser

ARTICLES_TO_POST = 5
RSS_URL = "http://feeds.feedburner.com/TechCrunch/"
TECHCRUNCH_URL = "https://techcrunch.com"

def get_tech_crunch_data() -> List[Dict[str, str]]:
    """
    Returns data from TechCrunch RSS feed
    """
    data = feedparser.parse(RSS_URL)
    if data.status != 200:
        return None
    return data.entries

def get_data_from_article(news: List[Dict[str, str]], index: int) -> Tuple[str, str]:
    """
    Returns the title of the article and the link

    Tuple returned: (title, url)
    """
    return (news[index]['title'], news[index]['link'])

@bot.on_command("techcrunch")
@loading_status
def handle_news(command: Command) -> None:
    """
    Prints the 5 top-most articles in the Latest News Section of TechCrunch
    using RSS feed
    """
    message = f"*------------------- Latest News from <{TECHCRUNCH_URL}|_TechCrunch_> " \
              f":newspaper: ---------------------*\n"
    news = get_tech_crunch_data()
    if news is None:
        bot.post_message(command.channel_id, "There was an error accessing "
                                             "TechCrunch RSS feed")
        return
    for i in range(ARTICLES_TO_POST):
        title, url = get_data_from_article(news, i)
        # Formats message a clickable headline which links to the article
        # These articles are also now bullet pointed
        message += f"• <{url}|{title}>\n\n"
    # Additional parameters ensure that the links don't show as big articles
    # underneath the input
    bot.post_message(command.channel_id, message, unfurl_links=False, unfurl_media=False)
