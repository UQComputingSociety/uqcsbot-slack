"""
Tests for umart.py
"""
from test.conftest import MockUQCSBot
from test.helpers import generate_message_object

NO_QUERY_MESSAGE = "You can't look for nothing. `!umart <QUERY>`"
NO_RESULTS_MESSAGE = "I can't find anything. Try `!umart <SOMETHING NOT AS SPECIFIC>`"
ERROR_MESSAGE = "I tried to get the things but alas I could not. Error with HTTP Request."

def test_umart_no_query(uqcsbot: MockUQCSBot):
    message = generate_message_object("!umart")
    uqcsbot.test_handle_event(message)
    assert len(uqcsbot.test_posted_messages) == 1
    assert uqcsbot.test_posted_messages[0].text == NO_QUERY_MESSAGE

def test_umart_normal(uqcsbot: MockUQCSBot):
    message = generate_message_object("!umart HDD")
    uqcsbot.test_handle_event(message)
    assert len(uqcsbot.test_posted_messages) == 1
    #Since the entire message from !umart is dynamic it is impossible to test for contents.