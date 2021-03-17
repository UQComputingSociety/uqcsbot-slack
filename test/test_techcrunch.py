from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch

import feedparser
from typing import List, Dict

def get_local_techcrunch_data() -> List[Dict[str, str]]:
    """
    Returns the RSS data from local mock copy of techcrunch xml.
    """
    try:
        with open("test/techcrunch.xml") as rawdata:
            data = feedparser.parse(rawdata.read()).entries
    except Exception as e:
        print("test/techcrunch.xml does not exist or cannot be opened")
        raise e
    return data

@patch("uqcsbot.scripts.techcrunch.get_tech_crunch_data", new=get_local_techcrunch_data)
def test_news(uqcsbot: MockUQCSBot):
    """
    Tests !techcrunch
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!techcrunch")
    message = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert (message[-1]['text'] ==
            "*Latest News from <https://techcrunch.com|_TechCrunch_> :techcrunch:*\n"
            "• <http://feedproxy.google.com/~r/Techcrunch/~3/99Ndo-D1yGA/|"
            "Rising encrypted app Signal is down in China>\n"
            "• <http://feedproxy.google.com/~r/Techcrunch/~3/CvyW_t3oxSQ/|"
            "China wants to dismantle Alibaba’s media empire: reports>\n"
            "• <http://feedproxy.google.com/~r/Techcrunch/~3/EqeGTrnZEYs/|"
            "Bird to spend $150 million on European expansion plan>\n"
            "• <http://feedproxy.google.com/~r/Techcrunch/~3/X98SDLR4A6Q/|"
            "Sherpa raises $8.5M to expand from conversational AI to B2B "
            "privacy-first federated learning services>\n"
            "• <http://feedproxy.google.com/~r/Techcrunch/~3/SdwlDvQPZHU/|"
            "Daily Crunch: Stripe valued at $95B>\n")
