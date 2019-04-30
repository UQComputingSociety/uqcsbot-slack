from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch
import xml.etree.ElementTree as ET


def mocked_xml_get(*args, **kwargs):
    """
    This method will be used to replace the requests response
    Returns locally stored XML Queensland forecasts from 2019.
    """
    source = {"NSW": "IDN11060", "ACT": "IDN11060", "NT": "IDD10207", "QLD": "IDQ11295", "SA": "IDS10044", "TAS": "IDT16710", "VIC": "IDV10753", "WA": "IDW14199"}
    try:
        data = open("test/bom_{}.xml".format(source[args[0]]))
        root = ET.fromstring(data.read())
    except:
        return None
    return root


@patch("uqcsbot.scripts.weather.get_xml", new=mocked_xml_get)
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
    for i in range(len(messages)-1, -1, -1):
        if messages[i]['text'].startswith("!weather"):
            messages.pop(i)

    assert len(messages) == 6
    for m in messages[1:]:
        assert m['text'] == messages[0]['text']

    assert messages[0]['text'].split("\r\n")[0] == "*Today's Weather Forcast For Brisbane*"


@patch("uqcsbot.scripts.weather.get_xml", new=mocked_xml_get)
def test_tomorrow(uqcsbot: MockUQCSBot):
    """
    Test !weather for tomorrow's Esk weather
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather Esk 1')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert messages[-1]['text'].split("\r\n")[0] == "*Tomorrow's Weather Forcast For Esk*"


@patch("uqcsbot.scripts.weather.get_xml", new=mocked_xml_get)
def test_location(uqcsbot: MockUQCSBot):
    """
    Test !weather for an multi word interstate location
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather NSW Coffs Harbour')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert messages[-1]['text'].split("\r\n")[0] == "*Today's Weather Forcast For Coffs Harbour*"


@patch("uqcsbot.scripts.weather.get_xml", new=mocked_xml_get)
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
