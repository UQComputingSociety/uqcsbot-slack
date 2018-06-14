from typing import List
from uqcsbot import bot, Command
from icalendar import Calendar, vText
import requests
from datetime import date, datetime, timedelta
from pytz import timezone, utc
import re

CALENDAR_URL = "https://calendar.google.com/calendar/ical/q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com" \
               "/public/basic.ics"
FILTER_REGEX = re.compile('(full|all|[0-9]+( weeks?)?)')
BRISBANE_TZ = timezone('Australia/Brisbane')
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


class EventFilter(object):
    def __init__(self, full=False, weeks=None, cap=None, is_valid=True):
        self.is_valid = is_valid
        self._full = full
        self._weeks = weeks
        self._cap = cap

    @classmethod
    def from_command(cls, command: Command):
        if not command.has_arg():
            return cls(weeks=2)
        else:
            match = re.match(FILTER_REGEX, command.arg)
            if not match:
                return cls(is_valid=False)
            filter_str = match.group(0)
            if filter_str in ['full', 'all']:
                return cls(full=True)
            elif 'week' in filter_str:
                return cls(weeks=int(filter_str.split()[0]))
            else:
                return cls(cap=int(filter_str))

    def filter_events(self, events: List['Event'], start_time: datetime):
        if self._weeks is not None:
            end_time = start_time + timedelta(weeks=self._weeks)
            return [e for e in events if e.start < end_time]
        elif self._cap is not None:
            return events[:self._cap]
        return events

    def get_header(self):
        if self._full:
            return "List of *all* upcoming events"
        elif self._weeks is not None:
            return f"Events in the *next _{self._weeks}_ weeks*"
        else:
            return f"The *next _{self._cap}_ events*"

    def get_no_result_msg(self):
        if self._weeks is not None:
            return f"There doesn't appear to be any events in the next *{self._weeks}* weeks"
        else:
            return "There doesn't appear to be any upcoming events..."


class Event(object):
    def __init__(self, start: datetime, end: datetime, location: vText, summary: vText):
        self.start = start
        self.end = end
        self.location = location
        self.summary = summary

    @classmethod
    def from_cal_event(cls, cal_event):
        start = cal_event.get('dtstart').dt
        end = cal_event.get('dtend').dt
        # ical 'dt' properties are parsed as a 'DDD' (datetime, date, duration)
        # type. The below code converts a date to a datetime, where time is set
        # to midnight.
        if isinstance(start, date) and not isinstance(start, datetime):
            start = datetime.combine(start, datetime.min.time()).astimezone(utc)
        if isinstance(end, date) and not isinstance(end, datetime):
            end = datetime.combine(end, datetime.max.time()).astimezone(utc)
        location = cal_event.get('location', 'TBA')
        summary = cal_event.get('summary')
        return cls(start, end, location, summary)

    def __str__(self):
        d1 = self.start.astimezone(BRISBANE_TZ)
        d2 = self.end.astimezone(BRISBANE_TZ)

        start_str = f"{MONTHS[d1.month-1]} {d1.day} {d1.hour}:{d1.minute:02}"
        if (d1.month, d1.day) != (d2.month, d2.day):
            end_str = f"{MONTHS[d2.month-1]} {d2.day} {d2.hour}:{d2.minute:02}"
        else:
            end_str = f"{d2.hour}:{d2.minute:02}"

        return f"*{start_str} - {end_str}* - _{self.location}_: `{self.summary}`"


@bot.on_command('events')
def handle_events(command: Command):
    '''
    `!events [full|all|NUM EVENTS|<NUM WEEKS> weeks]` - Lists all the UQCS
    events that are scheduled to occur within the given filter. If unspecified,
    will return the next 2 weeks of events.
    '''
    event_filter = EventFilter.from_command(command)
    if not event_filter.is_valid:
        bot.post_message(command.channel_id, "Invalid events filter.")
        return

    http_response = requests.get(CALENDAR_URL)
    cal = Calendar.from_ical(http_response.content)

    current_time = datetime.now(tz=BRISBANE_TZ).astimezone(utc)

    events = []
    # subcomponents are how icalendar returns the list of things in the calendar
    for c in cal.subcomponents:
        # TODO: support recurring events
        # we are only interested in ones with the name VEVENT as they are events
        # we also currently filter out recurring events
        if c.name != 'VEVENT' or c.get('RRULE') is not None:
            continue

        # we convert it to our own event class
        event = Event.from_cal_event(c)
        # then we want to filter out any events that are not after the current time
        if event.start > current_time:
            events.append(event)

    # then we apply our event filter as generated earlier
    events = event_filter.filter_events(events, current_time)
    # then, we sort the events by date
    events = sorted(events, key=lambda e: e.start)

    # then print to the user the result
    if not events:
        message = f"_{event_filter.get_no_result_msg()}_\r\n" \
                  f"For a full list of events, visit: https://uqcs.org.au/calendar.html"
    else:
        message = f"{event_filter.get_header()}\r\n" + '\r\n'.join(str(e) for e in events)

    bot.post_message(command.channel_id, message)
