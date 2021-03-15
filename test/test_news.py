from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch


def get_local_techcrunch_data() -> str:
    """
    Returns the local mock copy of techcrunch html
    """
    try:
        data = open("test/techcrunch.html").read()
    except Exception as e:
        raise e
        return (0, "")
    return (200, data)

@patch("uqcsbot.scripts.news.get_tech_crunch_data", new=get_local_techcrunch_data)
def test_news(uqcsbot : MockUQCSBot):
    """
    Tests !news
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!news")
    message = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert(message[-1]['text'] == 
            f"------------------------- Latest News from TechCrunch ---------------------------\n"
            f"<http://gmpg.org/xfn/11|http://gmpg.org/xfn/11>\n\n"
            f"<https://s.yimg.com/|//s.yimg.com>\n\n"
            f"<https://use.typekit.net/|//use.typekit.net>\n\n"
            f"<https://plugin.mediavoice.com/|//plugin.mediavoice.com>\n\n"
            f"<https://v0.wordpress.com/|//v0.wordpress.com>\n\n")
