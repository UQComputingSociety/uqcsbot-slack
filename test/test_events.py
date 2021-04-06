"""
Tests for the events module.
"""
from datetime import datetime
from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from pytz import timezone, utc
from unittest.mock import patch
from uqcsbot.utils.itee_seminar_utils import (HttpException, get_seminars)

BRISBANE_TZ = timezone('Australia/Brisbane')


def mocked_html_summary_get_typical() -> bytes:
    """
    Returns locally stored HTML that represents a typical seminar listing.
    """
    with open("test/ITEE_Upcoming_Seminars.html", "rb") as html_file:
        return html_file.read()


def mocked_html_summary_get_no_results() -> bytes:
    """
    Returns locally stored HTML that represents an empty seminar listing.
    """
    with open("test/ITEE_Upcoming_Seminars_empty.html", "rb") as html_file:
        return html_file.read()


def mocked_html_summary_get_error() -> bytes:
    """
    Throws an exception to indicate the seminar listing could not be loaded.
    """
    raise HttpException("SEMINAR-URL", 500)


def mocked_html_details_full(url: str) -> bytes:
    """
    Provides successful access to seminar details using locally stored content.
    """
    if url == "https://www.itee.uq.edu.au/introduction-functional-programming":
        with open("test/ITEE_Seminar1.html", "rb") as html_file:
            return html_file.read()
    if url == ("https://www.itee.uq.edu.au/performance-enhancement-software-defined"
               + "-cellular-5g-and-internet-things-networks"):
        with open("test/ITEE_Seminar2.html", "rb") as html_file:
            return html_file.read()
    assert False


def mocked_html_details_partial(url: str) -> bytes:
    """
    Provides partial access to seminar details using locally stored content.
    One endpoint works correctly, another reports a 500 server error.
    """
    if url == "https://www.itee.uq.edu.au/introduction-functional-programming":
        raise HttpException("SEMINAR-URL", 500)
    if url == ("https://www.itee.uq.edu.au/performance-enhancement-software-defined"
               + "-cellular-5g-and-internet-things-networks"):
        with open("test/ITEE_Seminar2.html", "rb") as html_file:
            return html_file.read()
    assert False


def mocked_events_ics(source: str = "uqcs") -> bytes:
    """
    Returns a locally stored .ics file that
    imitates the UQCS Calendar on Google Calendar.
    """
    with open("test/test_events_events.ics", "rb") as events_file:
        return events_file.read()

def mocked_get_august_2018_time():
    """
    Returns a fixed datetime at the start of August 2018.
    (Unline mocked_get_august_time the week after this date has a recurring event)
    """
    return datetime(2018, 8, 1, tzinfo=BRISBANE_TZ).astimezone(utc)

def mocked_get_august_time():
    """
    Returns a fixed datetime with events in the future.
    """
    return datetime(2019, 8, 1, tzinfo=BRISBANE_TZ).astimezone(utc)


def mocked_get_no_time():
    """
    Returns a fixed datetime without events in the future.
    """
    return datetime(2099, 8, 1, tzinfo=BRISBANE_TZ).astimezone(utc)


# unit tests of the Seminars component only
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_typical)
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_details_page",
       new=mocked_html_details_full)
def test_seminars_events_typical():
    """
    This test checks Seminar Utilities correctly provides seminar information
    when all ITEE website pages are available and correctly formatted.
    """
    summaries = get_seminars()
    brisbaneTime = timezone('Australia/Brisbane')
    expectedDate1 = datetime(2019, 5, 28, 12, 0, 0, tzinfo=brisbaneTime)
    expectedDate2 = datetime(2019, 5, 29, 13, 0, 0, tzinfo=brisbaneTime)

    assert len(summaries) == 2
    assert summaries[0] == ('Introduction to functional programming - Tony Morris, Software'
                            + ' Engineer at Data61',
                            'https://www.itee.uq.edu.au/introduction-functional-programming',
                            expectedDate1,
                            '78-420')
    assert summaries[1] == ('Performance Enhancement of Software Defined Cellular 5G &'
                            + ' Internet-of-Things Networks - Furqan Khan',
                            'https://www.itee.uq.edu.au/performance-enhancement-software'
                            + '-defined-cellular-5g-and-internet-things-networks',
                            expectedDate2,
                            '78-430')


@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_typical)
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_details_page",
       new=mocked_html_details_partial)
def test_seminars_events_partial_results():
    """
    This test checks Seminar Utilities correctly provides partial seminar information when the
    seminar listings page is available on the ITEE website, but not all of the details pages.
    """
    summaries = get_seminars()
    brisbaneTime = timezone('Australia/Brisbane')
    expectedDate1 = datetime(2019, 5, 28, 12, 0, 0, tzinfo=brisbaneTime)
    expectedDate2 = datetime(2019, 5, 29, 13, 0, 0, tzinfo=brisbaneTime)

    assert len(summaries) == 2
    assert summaries[0] == ('Introduction to functional programming',
                            'https://www.itee.uq.edu.au/introduction-functional-programming',
                            expectedDate1,
                            '78-420')
    assert summaries[1] == ('Performance Enhancement of Software Defined Cellular 5G &'
                            + ' Internet-of-Things Networks - Furqan Khan',
                            'https://www.itee.uq.edu.au/performance-enhancement-software'
                            + '-defined-cellular-5g-and-internet-things-networks',
                            expectedDate2,
                            '78-430')


@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_no_results)
def test_seminars_events_no_results():
    """
    This test checks Seminar Utilities correctly handles
    no seminars being listed on the ITEE website.
    """
    summaries = get_seminars()
    assert len(summaries) == 0


@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_error)
def test_seminar_events_seminars_error():
    """
    This test checks Seminar Utilities correctly handles the ITEE website being unavailable.
    The correct behaviour is to throw an exception.
    """
    try:
        get_seminars()
        assert False
    except HttpException as e:
        assert e.url == "SEMINAR-URL"
        assert e.status_code == 500


@patch("uqcsbot.scripts.events.get_calendar_file", new=mocked_events_ics)
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_typical)
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_details_page",
       new=mocked_html_details_full)
@patch("uqcsbot.scripts.events.get_current_time", new=mocked_get_no_time)
def test_seminar_events_typical(uqcsbot: MockUQCSBot):
    """
    This test simulates the user invoking !events when there are seminars available.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!events")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    expected = "_Events in the next *2 weeks*:_"
    assert messages[1].get('text') == expected


# unit tests of the UQCS events component only
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_no_results)
@patch("uqcsbot.scripts.events.get_calendar_file", new=mocked_events_ics)
@patch("uqcsbot.scripts.events.get_current_time", new=mocked_get_august_time)
def test_UQCS_events_typical(uqcsbot: MockUQCSBot):
    """
    This test simulates the user invoking `!events` when there are uqcs events.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!events")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    expected = "_Events in the next *2 weeks*:_"
    assert messages[1].get('text') == expected


@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_no_results)
@patch("uqcsbot.scripts.events.get_calendar_file", new=mocked_events_ics)
@patch("uqcsbot.scripts.events.get_current_time", new=mocked_get_august_time)
def test_UQCS_events_full(uqcsbot: MockUQCSBot):
    """
    This test simulates the user invoking `!events full` when there are uqcs events.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!events full")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    expected = "_List of *all* upcoming events:_"
    assert messages[1].get('text') == expected


@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_no_results)
@patch("uqcsbot.scripts.events.get_calendar_file", new=mocked_events_ics)
@patch("uqcsbot.scripts.events.get_current_time", new=mocked_get_august_time)
def test_UQCS_events_october(uqcsbot: MockUQCSBot):
    """
    This test simulates the user invoking `!events oct` when there are uqcs events.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!events oct")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    expected = "_Events in *October*:_"
    assert messages[1].get('text') == expected


# unit tests both seminars and UQCS events
@patch("uqcsbot.scripts.events.get_calendar_file", new=mocked_events_ics)
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_typical)
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_details_page",
       new=mocked_html_details_full)
@patch("uqcsbot.scripts.events.get_current_time", new=mocked_get_august_time)
def test_events_normal(uqcsbot: MockUQCSBot):
    """
    This test simulates the user invoking '!events', for both UQCS and Seminar calendars
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!events")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    expected = "_Events in the next *2 weeks*:_"
    assert messages[1].get('text') == expected


@patch("uqcsbot.scripts.events.get_calendar_file", new=mocked_events_ics)
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_error)
@patch("uqcsbot.scripts.events.get_current_time", new=mocked_get_no_time)
def test_events_no_events(uqcsbot: MockUQCSBot):
    """
    This test simulates the user invoking !events when there are no events available.
    The test cases includes the ITEE website being unavailable.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!events")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1].get('text') == ("_There don't appear to be any events"
                                       + " in the next *2* weeks_\n"
                                       "For a full list of events, visit:"
                                       + " https://uqcs.org/events"
                                       + " and https://www.itee.uq.edu.au/seminar-list")


def test_events_live(uqcsbot: MockUQCSBot):
    """
    This test simulates a user invoking '!events' against the live UQCS calendar
    and ITEE website. No particular assertion is made about the content of the
    bot's response, other than that there is one and it is not an error.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!events")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert (messages[1].get('text').startswith("_There don't appear to be any events"
                                               + " in the next *2* weeks_\n") or
            messages[1].get('text').startswith("_Events in the next *2 weeks*:_"))


# unit tests both seminars and UQCS events, filter to only UQCS events
@patch("uqcsbot.scripts.events.get_calendar_file", new=mocked_events_ics)
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_typical)
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_details_page",
       new=mocked_html_details_full)
@patch("uqcsbot.scripts.events.get_current_time", new=mocked_get_august_time)
def test_events_filter_uqcs(uqcsbot: MockUQCSBot):
    """
    This test simulates the user invoking '!events', for both UQCS and Seminar calendars
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!events uqcs")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    expected = "_Events in the next *2 weeks*:_"
    assert messages[1].get('text') == expected


# unit tests both seminars and UQCS events, filter to only ITEE events
@patch("uqcsbot.scripts.events.get_calendar_file", new=mocked_events_ics)
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_typical)
@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_details_page",
       new=mocked_html_details_full)
@patch("uqcsbot.scripts.events.get_current_time", new=mocked_get_august_time)
def test_events_filter_itee(uqcsbot: MockUQCSBot):
    """
    This test simulates the user invoking '!events', for both UQCS and Seminar calendars
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!events itee")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    expected = "_Events in the next *2 weeks*:_"
    assert messages[1].get('text') == expected

@patch("uqcsbot.utils.itee_seminar_utils.get_seminar_summary_page",
       new=mocked_html_summary_get_no_results)
@patch("uqcsbot.scripts.events.get_calendar_file", new=mocked_events_ics)
@patch("uqcsbot.scripts.events.get_current_time", new=mocked_get_august_2018_time)
def test_events_recurring(uqcsbot: MockUQCSBot):
    """
    This test simulates the user invoking '!events', to test for recurring events.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!events")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    expected = "*`[Recurring] deadbeef Binary Exploitation Bootcamp`*\n" \
        "*TUE AUG 7 18:30 - 20:00* _(78-346)_"
    assert messages[1].get('attachments')[2].get('blocks')[0].get('text').get('text') == expected
