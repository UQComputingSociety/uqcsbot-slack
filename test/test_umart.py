"""
Tests for umart.py
"""
from test.conftest import MockUQCSBot
from test.helpers import generate_message_object
from unittest import mock
import requests
import codecs

NO_QUERY_MESSAGE = "You can't look for nothing. `!umart <QUERY>`"
NO_RESULTS_MESSAGE = "I can't find anything. Try `!umart <SOMETHING NOT AS SPECIFIC>`"
ERROR_MESSAGE = "I tried to get the things but alas I could not. Error with HTTP Request."

TEST_URL = "https://www.umart.com.au/umart1/pro/products_list_searchnew_min.phtml?search=HDD&bid=2"

# This method will be used to replace the requests response
def mocked_html_get(*args, **kwargs):
    f = codecs.open("umart_products_list_search.html", "r")
    return f.read()


def test_umart_no_query(uqcsbot: MockUQCSBot):
    message = generate_message_object("!umart")
    uqcsbot.test_handle_event(message)
    assert len(uqcsbot.test_posted_messages) == 1
    assert uqcsbot.test_posted_messages[0].text == NO_QUERY_MESSAGE


@mock.patch("uqcsbot.scripts.umart.get_search_page", side_effect=mocked_html_get)
def test_umart_normal(uqcsbot: MockUQCSBot):
    message = generate_message_object("!umart HDD")
    uqcsbot.test_handle_event(message)
    assert len(uqcsbot.test_posted_messages) == 1