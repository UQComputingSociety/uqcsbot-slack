from uqcsbot import bot, Command
from requests.exceptions import RequestException
from typing import Dict, List
import requests

LEADERBOARD_URL = 'https://adventofcode.com/2018/leaderboard/private/view/'
LEADERBOARD_CODE = '246889'
# Session ID goes here
SESSION_ID = '' 

class Member:
    def __init__(self, name: str, score: int, stars: int) -> None:
        self.name = name
        self.score = score
        self.stars = stars

    def __lt__(self, other):
        return self.score > other.score or self.stars > other.stars

#@bot.on_schedule('cron', hour=15, timezone='Australia/Brisbane')
@bot.on_command("advent")
def advent(command: Command) -> None:
    '''
    Post the Advent of Code Leaderboard on #contests
    '''
    channel = bot.channels.get("contests")
    leaderboard = get_leaderboard()
    members = get_members(leaderboard['members'])

    message = "```\n"
    message += "Score Stars Name\n"
    for member in members:
        message += "{:5} {:5} {}\n".format(member.score, member.stars, member.name)
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
        url = "{}{}.json".format(LEADERBOARD_URL, LEADERBOARD_CODE)
        response = requests.get(url, cookies={"session": SESSION_ID})
        return response.json()
    except RequestException as e:
        bot.logger.error(e.response.content)
    return None
