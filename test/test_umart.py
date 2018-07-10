"""
Tests for umart.py
"""
from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch

NO_QUERY_MESSAGE = "You can't look for nothing. `!umart <QUERY>`"
NO_RESULTS_MESSAGE = "I can't find anything. Try `!umart <SOMETHING NOT AS SPECIFIC>`"
ERROR_MESSAGE = "I tried to get the things but alas I could not. Error with HTTP Request."

GOOD_MESSAGE = """```Name: <https://www.umart.com.au/umart1/pro/Product1|Product1>
Price: $1999.00
Name: <https://www.umart.com.au/umart1/pro/Product2|Product2>
Price: $1099.00
Name: <https://www.umart.com.au/umart1/pro/Product3|Product3>
Price: $1399.00
Name: <https://www.umart.com.au/umart1/pro/Product4|Product4>
Price: $1269.00
Name: <https://www.umart.com.au/umart1/pro/Product5|Product5>
Price: $1239.00
```"""


def mocked_html_get(*args, **kwargs):
    """
    This method will be used to replace the requests response
    Returns locally stored HTML that represents a typically scraped response.
    """
    f = open("test/umart_products_list_search.html", "r")
    return f.read()


def test_umart_no_query(uqcsbot: MockUQCSBot):
    """
    This test aims to determine the stability of the script when it receives no query.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!umart")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == NO_QUERY_MESSAGE


@patch("uqcsbot.scripts.umart.get_search_page", new=mocked_html_get)
def test_umart_normal(uqcsbot: MockUQCSBot):
    """
    This test aims to determine that a typical HTML response will result in a typical message.
    By mocking the get_search_page function with mocked_html_get
    no online functionality is required.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!umart HDD")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == GOOD_MESSAGE
