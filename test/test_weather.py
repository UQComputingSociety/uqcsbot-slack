from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch
import xml.etree.ElementTree as ET
import datetime


def mocked_xml_get(state):
    """
    This method will be used to replace the requests response
    Returns locally stored XML Queensland forecasts from 2019.
    """
    source = {"NSW": "IDN11060", "ACT": "IDN11060", "NT": "IDD10207", "QLD": "IDQ11295",
              "SA": "IDS10044", "TAS": "IDT16710", "VIC": "IDV10753", "WA": "IDW14199"}
    try:
        data = open("test/bom_{}.xml".format(source[state]))
        root = ET.fromstring(data.read())
    except Exception:
        return None
    return root


def mocked_response_header(node: ET.Element, location: str):
    """
    This method will be used to replace the header response
    Returns the header for 30th Aprl, 2019.
    """
    # write day name, "today" or "tomorrow"
    forcast_date = datetime.datetime.strptime(
        "".join(node.get('start-time-local')
                .rsplit(":", 1)), "%Y-%m-%dT%H:%M:%S%z"
        ).date()
    today_date = datetime.date(2019, 4, 30)
    date_delta = (forcast_date - today_date).days
    if date_delta == 0:
        date_name = "Today"
    elif date_delta == 1:
        date_name = "Tomorrow"
    elif date_delta == -1:
        # can happen during the witching hours
        date_name = "Yesterday"
    else:
        date_name = forcast_date.strftime("%A")
    return "*{}'s Weather Forcast For {}*".format(date_name, location)


@patch("uqcsbot.scripts.weather.get_xml", new=mocked_xml_get)
@patch("uqcsbot.scripts.weather.response_header", new=mocked_response_header)
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
@patch("uqcsbot.scripts.weather.response_header", new=mocked_response_header)
def test_tomorrow(uqcsbot: MockUQCSBot):
    """
    Test !weather for tomorrow's Esk weather
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather Esk 1')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert messages[-1]['text'].split("\r\n")[0] == "*Tomorrow's Weather Forcast For Esk*"


@patch("uqcsbot.scripts.weather.get_xml", new=mocked_xml_get)
@patch("uqcsbot.scripts.weather.response_header", new=mocked_response_header)
def test_location(uqcsbot: MockUQCSBot):
    """
    Test !weather for an multi word interstate location
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather NSW Coffs Harbour')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert messages[-1]['text'].split("\r\n")[0] == "*Today's Weather Forcast For Coffs Harbour*"


@patch("uqcsbot.scripts.weather.get_xml", new=mocked_xml_get)
@patch("uqcsbot.scripts.weather.response_header", new=mocked_response_header)
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

    uqcsbot.post_message(TEST_CHANNEL_ID, '!weather TAS Hobart')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert messages[-1]['text'] == "Could Not Retrieve BOM Data"
