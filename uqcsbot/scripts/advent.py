from types import FunctionType
from uqcsbot import bot, Command
from uqcsbot.api import Channel
from uqcsbot.utils.command_utils import loading_status, UsageSyntaxException

from argparse import ArgumentError, ArgumentParser, Namespace
from datetime import datetime, timedelta, timezone
from requests.exceptions import RequestException
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum
import os
import requests

# Leaderboard API URL with placeholders for year and code.
LEADERBOARD_URL = 'https://adventofcode.com/{year}/leaderboard/private/view/{code}.json'
# Session cookie (will expire in approx 30 days).
SESSION_ID = os.environ.get('AOC_SESSION_ID')
# UQCS leaderboard ID.
UQCS_LEADERBOARD = 989288

# Days in Advent of Code. List of numbers 1 to 25.
ADVENT_DAYS = list(range(1, 25 + 1))
# Puzzles are unlocked at midnight EST.
EST_TIMEZONE = timezone(timedelta(hours=-5))

class SortMode(Enum):
    """Options for sorting the leaderboard."""
    PART_1 = 'p1'
    PART_2 = 'p2'
    DELTA = 'delta'
    SCORE = 'score' # SORT_SCORE is not shown to users

# Map of sorting options to friendly name.
SORT_LABELS = {
    SortMode.PART_1: 'part 1 completion',
    SortMode.PART_2: 'part 2 completion',
    SortMode.DELTA: 'time delta',
}


def sort_none_last(key):
    """
    Given sort key function, returns new key function which can handle None.

    None values are sorted after non-None values.
    """
    return lambda x: (key(x) is None, key(x))

# type aliases for documentation purposes.
Star = int # from 1 to 25
Day = int # 1 or 2
Seconds = int
DayTimes = Dict[Day, Dict[Star, Seconds]]
DayDeltas = Dict[Day, Optional[Seconds]]
# TODO: make these types more specific with TypedDict and Literal when possible.

class Member:
    def __init__(self, name: str, score: int, stars: int) -> None:
        self.name = name
        self.score = score
        self.stars = stars
        # maps day to 
        self.day_times: DayTimes = {d: {} for d in ADVENT_DAYS}
        self.day_deltas: DayDeltas = {d: None for d in ADVENT_DAYS}
    
    @classmethod 
    def from_member_data(cls, data: Dict, year: int):
        """Constructs a Member from the API response."""

        member = cls(data['name'], data['local_score'], data['stars'])

        for day, day_data in data['completion_day_level'].items():
            day = int(day)
            day_times = member.day_times[day]

            # timestamp of puzzle unlock, rounded to whole seconds
            DAY_START = int(
                datetime(year, 12, day, tzinfo=EST_TIMEZONE).timestamp())

            for star, star_data in day_data.items():
                star = int(star)
                day_times[star] = int(star_data['get_star_ts']) - DAY_START

            if len(day_times) == 2:
                part_1, part_2 = sorted(day_times.values())
                member.day_deltas[day] = part_2 - part_1

        return member

    @staticmethod 
    def sort_key(sort: SortMode, day: int=None) -> Callable[['Member'], Any]:
        """
        Given sort mode and day, returns a key function which sorts members
        by that option on that day.
        """

        if sort == SortMode.SCORE:
            # sorts by score, then stars, descending.
            return lambda m: (-m.score, -m.stars)
        
        # if we get here, we have a day-specific sort. require day parameter.
        assert day is not None

        # these key functions sort in ascending order of the specified value.
        if sort == SortMode.PART_1:
            key = lambda m: m.day_times[day].get(1)
        elif sort == SortMode.PART_2:
            key = lambda m: m.day_times[day].get(2)
        elif sort == SortMode.DELTA:
            key = lambda m: m.day_deltas[day]
        else:
            assert False

        return sort_none_last(key)


def star_char(num_stars: int):
    """Given a number of stars (0, 1, or 2), returns its leaderboard
    representation."""
    if num_stars == 0: 
        return ' '
    elif num_stars == 1:
        return '.'
    elif num_stars == 2:
        return '*'
    assert False

def format_full_leaderboard(members: List[Member]) -> str:
    """
    Returns a string representing the full leaderboard of the given list.

    Full leaderboard includes rank, points, stars (per day), and username.
    """

    #  3     4                        25
    #|-|  |--| |-----------------------|
    #  1)  751 ****************          Name
    def format_member(i: int, m: Member):
        stars = ''.join(star_char(len(m.day_times[d])) for d in ADVENT_DAYS)
        return f'{i:>3}) {m.score:>4} {stars} {m.name}'

    left_pad = ' ' * (3 + 2 + 4 + 1) # chars before stars start
    header = (left_pad + '         1111111111222222\n' 
        + left_pad + '1234567890123456789012345\n')

    return header + '\n'.join(
        format_member(i+1, m) for i, m in enumerate(members))


def format_day_leaderboard(members: List[Member], day: int) -> str:
    """
    Returns a string representing the leaderboard of the given members on
    the given day.

    Full leaderboard includes rank, points, stars (per day), and username.
    """

    def format_seconds(seconds: int):
        if not seconds: 
            return ''
        delta = timedelta(seconds=seconds)
        if delta > timedelta(hours=24):
            return '>24h'
        return str(delta)

    #  3         8        8         8
    #|-|  |------| |------|  |------|
    #      Part 1   Part 2     Delta 
    #  1)  0:00:00  0:00:00   0:00:00  Name 1
    #  2)     >24h     >24h      >24h  Name 2
    def format_member(i: int, m: Member):
        part_1 = format_seconds(m.day_times[day].get(1))
        part_2 = format_seconds(m.day_times[day].get(2))
        delta = format_seconds(m.day_deltas[day])
        return f'{i:>3}) {part_1:>8} {part_2:>8}  {delta:>8}  {m.name}'

    header = '       Part 1   Part 2     Delta\n'
    return header + '\n'.join(
        format_member(i+1, m) for i, m in enumerate(members))


def format_advent_leaderboard(members: List[Member], 
                              day: int, sort: SortMode) -> str:
    """
    Returns a leaderboard for the given members with the given options.

    If day is non-zero, the leaderboard is for that day only.
    """

    # if no day is specified, show full leaderboard of all days
    if not day: 
        members.sort(key=Member.sort_key(SortMode.SCORE))
        return format_full_leaderboard(members)
    else:
        # filter to users who have at least one star on this day.
        members = [m for m in members if m.day_times[day]]
        members.sort(key=Member.sort_key(sort, day))
        return format_day_leaderboard(members, day)


def parse_arguments(argv: List[str]) -> Namespace:

    parser = ArgumentParser('!advent', add_help=False)

    parser.add_argument('day', type=int, default=0, nargs='?',
                        help='Show leaderboard for specific day ' + 
                            '(default: all days)')
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year of leaderboard (default: current year)')
    parser.add_argument('-c', '--code', type=int, default=UQCS_LEADERBOARD,
                        help='Leaderboard code (default: UQCS leaderboard)')
    parser.add_argument('-s', '--sort', default=SortMode.PART_2,
                        choices=(SortMode.PART_1, SortMode.PART_2, 
                            SortMode.DELTA),
                        help='Sorting method when displaying one day ' + 
                            '(default: part 2 completion time)')
    parser.add_argument('-h', '--help', action='store_true', 
                        help='Prints this help message')

    # used to propagate usage errors out
    def usage_error(message, *args, **kwargs):
        raise UsageSyntaxException(message)
    parser.error = usage_error # type: ignore

    args = parser.parse_args(argv)
    
    if args.help:
        raise UsageSyntaxException('```\n' + parser.format_help() + '\n```')

    return args


@bot.on_command('advent')
@loading_status
def advent(command: Command) -> None:
    """
    !advent - Prints the Advent of Code private leaderboard for UQCS
    """

    channel = bot.channels.get(command.channel_id, use_cache=False)
    
    def reply(message):
        bot.post_message(channel, message, thread_ts=command.thread_ts)

    try:
        args = parse_arguments(
            command.arg.split() if command.has_arg() else [])
    except UsageSyntaxException as error:
        reply(str(error))
        return

    # do not continue if args is unset, e.g. due to --help
    if not args:
        return

    try:
        leaderboard = get_leaderboard(args.year, args.code)
    except ValueError:
        reply('Error fetching leaderboard data. ' 
            'Check the leaderboard code, year, and day.')
        raise

    try:
        members = [Member.from_member_data(data, args.year)
            for data in leaderboard['members'].values()]
    except Exception:
        reply('Error parsing leaderboard data.')
        raise

    # header message
    message = f':star: *Advent of Code Leaderboard {args.code}* :trophy:'
    if args.day:
        message += (
            f'\n:calendar: *Day {args.day}* ' 
            f'(sorted by {SORT_LABELS[args.sort]})'
        )
    
    # reply with leaderboard as a file attachment because it gets quite large.
    bot.api.files.upload(
        initial_comment=message,
        content=format_advent_leaderboard(
            members, args.day, args.sort),
        title=f'advent_{args.code}_{args.year}_{args.day}.txt',
        filetype='text',
        channels=channel.id,
        thread_ts=command.thread_ts
    )


def get_leaderboard(year: int, code: int) -> Dict:
    """
    Returns a json dump of the leaderboard
    """
    try:
        response = requests.get(
            LEADERBOARD_URL.format(year=year, code=code), 
            cookies={'session': SESSION_ID})
        return response.json()
    except ValueError as exception: #  json.JSONDecodeError
        # TODO: Handle the case when the response is ok but the contents
        # are invalid (cannot be parsed as json)
        raise exception
    except RequestException as exception:
        bot.logger.error(exception.response.content)
    return None
