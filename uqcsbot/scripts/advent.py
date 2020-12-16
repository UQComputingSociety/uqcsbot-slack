from uqcsbot import bot, Command
from uqcsbot.api import Channel
from uqcsbot.utils.command_utils import loading_status, UsageSyntaxException

from argparse import ArgumentError, ArgumentParser, Namespace
from datetime import datetime, timedelta
from requests.exceptions import RequestException
from typing import Dict, List
import os
import requests


LEADERBOARD_URL = "https://adventofcode.com/{year}/leaderboard/private/view/{code}.json"
SESSION_ID = os.environ["AOC_SESSION_ID"] 
UQCS_LEADERBOARD = 989288

ADVENT_DAYS = list(range(1, 25 + 1))

SORT_PART_1 = 'p1'
SORT_PART_2 = 'p2'
SORT_DELTA = 'delta'


class Member:
    def __init__(self, name: str, score: int, stars: int) -> None:
        self.name = name
        self.score = score
        self.stars = stars
        self.day_times = {d: [] for d in ADVENT_DAYS}
        self.day_deltas = {d: None for d in ADVENT_DAYS}
    
    @classmethod 
    def from_member_data(cls, data):
        member = cls(data['name'], data['local_score'], data['stars'])

        for day, day_data in data['completion_day_level'].items():
            day = int(day)
            # sort so part 1 is added before part 2
            for star, star_data in sorted(day_data.items()):
                star = int(star)
                member.day_times[day].append(
                    datetime.fromtimestamp(int(star_data['get_star_ts'])))

                if star == 2:
                    part_1, part_2 = member.day_times[day]
                    member.day_deltas[day] = part_2 - part_1

        return member

def parse_arguments(channel: Channel, argv: List[str]) -> Namespace:
    parser = ArgumentParser('!advent', add_help=False)

    def usage_error(message, *args, **kwargs):
        raise ArgumentError(None, message)

    parser.add_argument('day', type=int, default=0, nargs='?',
                        help='Show leaderboard for specific day ' + 
                            '(default: all days)')
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year of leaderboard (default: current year)')
    parser.add_argument('-c', '--code', type=int, default=UQCS_LEADERBOARD,
                        help='Leaderboard code (default: UQCS leaderboard)')
    parser.add_argument('-s', '--sort', 
                        choices=(SORT_PART_1, SORT_PART_2, SORT_DELTA),
                        help='Sorting method when displaying one day ' + 
                            '(default: part 2 completion time)')
    parser.add_argument('-h', '--help', action='store_true', 
                        help='Prints this help message')

    parser.error = usage_error

    args = parser.parse_args(argv.split())
    
    if args.help:
        bot.post_message(channel, parser.format_help())
        return None

    return args

def star_char(num_stars: int):
    if num_stars == 0: 
        return ' '
    elif num_stars == 1:
        return '.'
    elif num_stars == 2:
        return '*'
    assert False

def format_full_leaderboard(members: List[Member]) -> str:
    def format_member(i: int, m: Member):
        stars = ''.join(star_char(len(m.day_times[d])) for d in ADVENT_DAYS)
        return f'{i:>3}) {m.score:>4} {stars} {m.name}'

    left_pad = ' ' * (3 + 2 + 4 + 1) # chars before stars start
    header = (left_pad + '         1111111111222222\n' 
        + left_pad + '1234567890123456789012345\n')

    return header + '\n'.join(format_member(i+1, m) for i, m in enumerate(members))


@bot.on_command("advent")
@loading_status
def advent(command: Command) -> None:
    """
    !advent - Prints the Advent of Code private leaderboard for UQCS
    """
    channel = bot.channels.get(command.channel_id, use_cache=False)
    
    try:
        args = parse_arguments(channel, command.arg if command.has_arg() else '')
    except ArgumentError as error:
        bot.post_message(channel, error.message)
        args = None
    if not args:
        return

    try:
        leaderboard = get_leaderboard(args.year, args.code)
    except ValueError:
        bot.post_message(channel, 'Error fetching leaderboard data. ' 
            'Check the leaderboard code, year, and day.')
        raise
    members = [Member.from_member_data(data) for data in leaderboard["members"].values()]
    message = '**:star: Advent of Code Leaderboard :trophy:**'

    if not args.day: 
        members.sort(key=lambda m: (m.score, m.stars), reverse=True)
        message += "\n```\n" + format_full_leaderboard(members) + "```"
    else:
        message += f' (Day {args.day})\n'

    bot.post_message(command.channel_id, message)


def get_leaderboard(year: int, code: int) -> Dict:
    """
    Returns a json dump of the leaderboard
    """
    try:
        response = requests.get(
            LEADERBOARD_URL.format(year=year, code=code), 
            cookies={"session": SESSION_ID})
        return response.json()
    except ValueError as exception: #  json.JSONDecodeError
        # TODO: Handle the case when the response is ok but the contents
        # are invalid (cannot be parsed as json)
        raise exception
    except RequestException as exception:
        bot.logger.error(exception.response.content)
    return None
