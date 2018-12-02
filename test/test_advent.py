import requests
from uqcsbot.scripts import advent


def test_advent_normal():
    """
    Tests that the private leaderboard can be accessed and the
    JSON structure can be parsed
    """
    response = requests.get(advent.LEADERBOARD_URL, cookies={"session": advent.SESSION_ID})

    assert response.status_code == 200
    assert response.json()
    assert response.json()['members']
