import os
import requests

# TODO: Move the LEADERBOARD_URL and SESSION_ID someplace else to miniize duplication
LEADERBOARD_URL = 'https://adventofcode.com/2018/leaderboard/private/view/246889.json'
SESSION_ID = os.environ['AOC_SESSION_ID']


def test_advent_normal():
    """
    Tests that the private leaderboard can be accessed and the
    JSON structure can be parsed
    """
    response = requests.get(LEADERBOARD_URL, cookies={"session": SESSION_ID})

    assert response.status_code == 200
    assert response.json()
    assert response.json()['members']
