from typing import List
import re
from datetime import date, datetime, timedelta
from calendar import month_name, month_abbr, day_abbr
from icalendar import Calendar
import requests
from pytz import timezone, utc
from typing import Tuple, Optional
from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import UsageSyntaxException, loading_status
from uqcsbot.utils.itee_seminar_utils import (get_seminars, HttpException, InvalidFormatException)

CALENDAR_URL = ("https://calendar.google.com/calendar/ical/"
                + "q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com/public/basic.ics")
FILTER_REGEX = re.compile('full|all|[0-9]+( weeks?)?|jan.*|feb.*|mar.*'
                          + '|apr.*|may.*|jun.*|jul.*|aug.*|sep.*|oct.*|nov.*|dec.*')
BRISBANE_TZ = timezone('Australia/Brisbane')
# empty string to one-index
MONTH_NUMBER = {month.lower(): index for index, month in enumerate(month_abbr)}


class EventFilter(object):
    def __init__(self, full=False, weeks=None, cap=None, month=None, is_valid=True):
        self.is_valid = is_valid
        self._full = full
        self._weeks = weeks
        self._cap = cap
        self._month = month

    @classmethod
    def from_argument(cls, argument: str):
        if not argument:
            return cls(weeks=2)
        else:
            match = re.match(FILTER_REGEX, argument.lower())
            if not match:
                return cls(is_valid=False)
            filter_str = match.group(0)
            if filter_str in ['full', 'all']:
                return cls(full=True)
            elif 'week' in filter_str:
                return cls(weeks=int(filter_str.split()[0]))
            elif filter_str[:3] in MONTH_NUMBER:
                return cls(month=MONTH_NUMBER[filter_str[:3]])
            else:
                return cls(cap=int(filter_str))

    def filter_events(self, events: List['Event'], start_time: datetime):
        if self._weeks is not None:
            end_time = start_time + timedelta(weeks=self._weeks)
            return [e for e in events if e.start < end_time]
        if self._month is not None:
            return [e for e in events if e.start.month == self._month]
        elif self._cap is not None:
            return events[:self._cap]
        return events

    def get_header(self):
        if self._full:
            return "List of *all* upcoming events"
        elif self._weeks is not None:
            return f"Events in the *next _{self._weeks}_ weeks*"
        elif self._month is not None:
            return f"Events in *_{month_name[self._month]}_*"
        else:
            return f"The *next _{self._cap}_ events*"

    def get_no_result_msg(self):
        if self._weeks is not None:
            return f"There don't appear to be any events in the next *{self._weeks}* weeks"
        elif self._month is not None:
            return f"There don't appear to be any events in *{month_name[self._month]}*"
        else:
            return "There don't appear to be any upcoming events..."


class Event(object):
    def __init__(self, start: datetime, end: datetime,
                 location: str, summary: str, link: Optional[str]):
        self.start = start
        self.end = end
        self.location = location
        self.summary = summary
        self.link = link

    @classmethod
    def encode_text(cls, text: str) -> str:
        """
        Encodes user-specified text so that it is not interpreted as command characters
        by Slack. Implementation as required by: https://api.slack.com/docs/message-formatting
        Note that this encoding process does not stop injection of text effects (bolding,
        underlining, etc.), or a malicious user breaking the text formatting in the events
        command. It should, however, prevent <, & and > being misinterpreted and including
        links where they should not.
        --
        :param text: The text to encode
        :return: The encoded text
        """
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    @classmethod
    def from_cal_event(cls, cal_event):
        start = cal_event.get('dtstart').dt
        end = cal_event.get('dtend').dt
        # ical 'dt' properties are parsed as a 'DDD' (datetime, date, duration) type.
        # The below code converts a date to a datetime, where time is set to midnight.
        if isinstance(start, date) and not isinstance(start, datetime):
            start = datetime.combine(start, datetime.min.time()).astimezone(utc)
        if isinstance(end, date) and not isinstance(end, datetime):
            end = datetime.combine(end, datetime.max.time()).astimezone(utc)
        location = cal_event.get('location', 'TBA')
        summary = cal_event.get('summary')
        return cls(start, end, location, summary, None)

    @classmethod
    def from_seminar(cls, seminar_event: Tuple[str, str, datetime, str]):
        title, link, start, location = seminar_event
        # ITEE doesn't specify the length of seminars, but they are normally one hour
        end = start + timedelta(hours=1)
        # Note: this
        return cls(start, end, location, title, link)

    def __str__(self):
        d1 = self.start.astimezone(BRISBANE_TZ)
        d2 = self.end.astimezone(BRISBANE_TZ)

        start_str = (f"{day_abbr[d1.weekday()].upper()}"
                     + f" {month_abbr[d1.month].upper()} {d1.day} {d1.hour}:{d1.minute:02}")
        if (d1.month, d1.day) != (d2.month, d2.day):
            end_str = (f"{day_abbr[d2.weekday()].upper()}"
                       + f" {month_abbr[d2.month].upper()} {d2.day} {d2.hour}:{d2.minute:02}")
        else:
            end_str = f"{d2.hour}:{d2.minute:02}"

        # Encode user-provided text to prevent certain characters
        # being interpreted as slack commands.
        summary_str = Event.encode_text(self.summary)
        location_str = Event.encode_text(self.location)

        if self.link is None:
            return f"*{start_str} - {end_str}* - `{summary_str}` - _{location_str}_"
        else:
            return f"*{start_str} - {end_str}* - `<{self.link}|{summary_str}>` - _{location_str}_"


def get_current_time():
    """
    returns the current date and time
    this function exists purely so it can be mocked for testing
    """
    return datetime.now(tz=BRISBANE_TZ).astimezone(utc)


@bot.on_command('events')
@loading_status
def handle_events(command: Command):
    """
    `!events [full|all|NUM EVENTS|<NUM WEEKS> weeks] [uqcs|itee]`
    - Lists all the UQCS and/or  ITEE events that are
    scheduled to occur within the given filter.
    If unspecified, will return the next 2 weeks of events.
    """

    argument = command.arg if command.has_arg() else ""

    source_get = {"uqcs": False, "itee": False}
    for k in source_get:
        if k in argument:
            source_get[k] = True
            argument = argument.replace(k, "")
    argument = argument.strip()
    if not any(source_get.values()):
        source_get = dict.fromkeys(source_get, True)

    event_filter = EventFilter.from_argument(argument)
    if not event_filter.is_valid:
        raise UsageSyntaxException()

    cal = Calendar.from_ical(get_calendar_file())
    current_time = get_current_time()

    events = []
    # subcomponents are how icalendar returns the list of things in the calendar
    if source_get["uqcs"]:
        for c in cal.subcomponents:
            # TODO: support recurring events
            # we are only interested in ones with the name VEVENT as they
            # are events we also currently filter out recurring events
            if c.name != 'VEVENT' or c.get('RRULE') is not None:
                continue

            # we convert it to our own event class
            event = Event.from_cal_event(c)
            # then we want to filter out any events that are not after the current time
            if event.start > current_time:
                events.append(event)

    if source_get["itee"]:
        try:
            # Try to include events from the ITEE seminars page
            seminars = get_seminars()
            for seminar in seminars:
                # The ITEE website only lists current events.
                event = Event.from_seminar(seminar)
                events.append(event)
        except (HttpException, InvalidFormatException) as e:
            bot.logger.error(e.message)

    # then we apply our event filter as generated earlier
    events = event_filter.filter_events(events, current_time)
    # then, we sort the events by date
    events = sorted(events, key=lambda e: e.start)

    # then print to the user the result
    if not events:
        message = (f"_{event_filter.get_no_result_msg()}_\r\n"
                   "For a full list of events, visit: https://uqcs.org.au/calendar.html"
                   + " and https://www.itee.uq.edu.au/seminar-list")
    else:
        message = f"{event_filter.get_header()}\r\n" + '\r\n'.join(str(e) for e in events)

    bot.post_message(command.channel_id, message)


def get_calendar_file() -> bytes:
    """
    Loads the UQCS Events calender .ics file from Google Calendar.
    This method is mocked by unit tests.
    :return: The returned ics calendar file, as a stream
    """
    http_response = requests.get(CALENDAR_URL)
    return http_response.content
