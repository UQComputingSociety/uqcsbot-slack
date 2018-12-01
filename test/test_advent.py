import requests

# TODO: Move the LEADERBOARD_CODE and SESSION_ID someplace else to miniize duplication
LEADERBOARD_URL = 'https://adventofcode.com/2018/leaderboard/private/view/'
LEADERBOARD_CODE = '246889'
# Session ID goes here
SESSION_ID = ''


def test_advent_normal():
    """
    Tests that the private leaderboard can be accessed and the
    JSON structure can be parsed
    """
    url = "{}{}.json".format(LEADERBOARD_URL, LEADERBOARD_CODE)
    response = requests.get(url, cookies={"session": SESSION_ID})

    assert response.status_code == 200
    assert response.json()
    assert response.json()['members']
