from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
from requests.exceptions import RequestException
from typing import Dict, List
import os
import requests

LEADERBOARD_URL = 'https://adventofcode.com/2018/leaderboard/private/view/246889.json'
SESSION_ID = os.environ['AOC_SESSION_ID'] 


class Member:
    def __init__(self, name: str, score: int, stars: int) -> None:
        self.name = name
        self.score = score
        self.stars = stars

    def __lt__(self, other):
        return self.score > other.score or (self.score == other.score and self.stars > other.stars)

#@bot.on_schedule('cron', hour=15, timezone='Australia/Brisbane')
@bot.on_command("advent")
@loading_status
def advent(command: Command) -> None:
    '''
    !advent - Prints the Advent of Code private leaderboard for UQCS
    '''
    channel = bot.channels.get("contests")

    leaderboard = get_leaderboard()
    members = get_members(leaderboard['members'])

    message = "```\n"
    message += "Score Stars Name\n"
    for member in members:
        message += f'{member.score:5} {member.stars:5} {member.name}\n'
    message += "```"

    bot.post_message(command.channel_id, message)

def get_members(members_json: Dict) -> List[Member]:
    '''
    Returns a sorted list of Members in the leaderboard
    '''
    members = []

    for member in members_json.values():
        members.append(
                Member(member['name'], member['local_score'], member['stars']))

    members.sort()
    return members

def get_leaderboard() -> Dict:
    '''
    Returns a json dump of the leaderboard
    '''
    try:
        response = requests.get(LEADERBOARD_URL, cookies={"session": SESSION_ID})
        return response.json()
    except ValueError as exception: #  json.JSONDecodeError
        # TODO: Handle the case when the response is ok but the contents
        # are invalid (cannot be parsed as json)
        raise exception
    except RequestException as exception:
        bot.logger.error(exception.response.content)
    return None
