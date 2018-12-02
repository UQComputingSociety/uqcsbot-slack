import requests
from uqcsbot.scripts.advent import LEADERBOARD_URL, SESSION_ID, Member


def test_advent_normal():
    """
    Tests that the private leaderboard can be accessed and that the
    JSON structure can be parsed
    """
    response = requests.get(LEADERBOARD_URL, cookies={"session": SESSION_ID})

    assert response.status_code == 200
    assert response.json()
    assert response.json()['members']


def test_advent_member_sort():
    """
    Tests that the comparator function on Member is sane
    """
    sorted_names = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot']

    members = [
            Member('delta', 20, 10),
            Member('bravo', 20, 20),
            Member('alpha', 30, 30),
            Member('foxtrot', 10, 10),
            Member('charlie', 20, 20),
            Member('echo', 10, 40)]
    members.sort()

    assert [member.name for member in members] == sorted_names
