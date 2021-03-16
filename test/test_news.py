from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch

import feedparser
from typing import List, Dict

def get_local_techcrunch_data() -> List[Dict[str, str]]:
    """
    Returns the RSS data from local mock copy of techcrunch xml
    """
    try:
        rawdata = open("test/techcrunch.xml").read()
        data = feedparser.parse(rawdata).entries
    except Exception as e:
        raise e
        return (0, "")
    return data

@patch("uqcsbot.scripts.news.get_tech_crunch_data", new=get_local_techcrunch_data)
def test_news(uqcsbot: MockUQCSBot):
    """
    Tests !news
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!news")
    message = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert(message[-1]['text'] ==
            "------------------------- Latest News from TechCrunch ---------------------------\n"
            "<http://feedproxy.google.com/~r/Techcrunch/~3/99Ndo-D1yGA/|"
            "Rising encrypted app Signal is down in China>\n\n"
            "<http://feedproxy.google.com/~r/Techcrunch/~3/CvyW_t3oxSQ/|"
            "China wants to dismantle Alibaba’s media empire: reports>\n\n"
            "<http://feedproxy.google.com/~r/Techcrunch/~3/EqeGTrnZEYs/|"
            "Bird to spend $150 million on European expansion plan>\n\n"
            "<http://feedproxy.google.com/~r/Techcrunch/~3/X98SDLR4A6Q/|"
            "Sherpa raises $8.5M to expand from conversational AI to B2B "
            "privacy-first federated learning services>\n\n"
            "<http://feedproxy.google.com/~r/Techcrunch/~3/SdwlDvQPZHU/|"
            "Daily Crunch: Stripe valued at $95B>\n\n")
