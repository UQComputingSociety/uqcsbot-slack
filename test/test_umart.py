"""
Tests for umart.py
"""
from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch
import codecs

NO_QUERY_MESSAGE = "You can't look for nothing. `!umart <QUERY>`"
NO_RESULTS_MESSAGE = "I can't find anything. Try `!umart <SOMETHING NOT AS SPECIFIC>`"
ERROR_MESSAGE = "I tried to get the things but alas I could not. Error with HTTP Request."

TEST_URL = "https://www.umart.com.au/umart1/pro/products_list_searchnew_min.phtml?search=HDD&bid=2"


def get_test_message():
    f = codecs.open("test/umart_test_message.txt", "r")
    return f.read()

# This method will be used to replace the requests response


def mocked_html_get(*args, **kwargs):
    f = codecs.open("test/umart_products_list_search.html", "r")
    return f.read()


def test_umart_no_query(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!umart")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == NO_QUERY_MESSAGE


@patch("uqcsbot.scripts.umart.get_search_page", new=mocked_html_get)
def test_umart_normal(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!umart HDD")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == get_test_message()
