from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_brisbane(uqcsbot: MockUQCSBot):
    """
    Tests all varients !weather that give today's Brisbane weather
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather')
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather Brisbane')
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather QLD Brisbane')
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather 0')
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather Brisbane 0')
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather QLD Brisbane 0')
    
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    for i in range(len(messages)-1,-1,-1):
        if messages[i]['text'].startswith("!weather"):
            messages.pop(i)

    assert len(messages) == 6
    for m in messages[1:]:
        assert m['text'] == messages[0]['text']

    assert messages[0]['text'].split("\r\n")[0] == "*Today's Weather Forcast For Brisbane*"

def test_tomorrow(uqcsbot: MockUQCSBot):
    """
    Test !weather for tomorrows's Esk weather
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather Esk 1')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert messages[-1]['text'].split("\r\n")[0] == "*Tomorrow's Weather Forcast For Esk*"

def test_location(uqcsbot: MockUQCSBot):
    """
    Test !weather for an multi word interstate location
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather NSW Coffs Harbour')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert messages[-1]['text'].split("\r\n")[0] == "*Today's Weather Forcast For Coffs Harbour*"

def test_error(uqcsbot: MockUQCSBot):
    """
    Test !weather for error messages
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather nowhere')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert messages[-1]['text'] == "Location Not Found"
    
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather -1')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert messages[-1]['text'] == "No Forecast Available For That Day"
