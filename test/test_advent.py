import json
from typing import List
from uqcsbot.scripts.advent import Member, SortMode, format_advent_leaderboard, \
    format_day_leaderboard, format_full_leaderboard

with open('./test/advent_test_data.json', encoding='utf-8') as f:
    ADVENT_TEST_DATA = json.load(f)

# remark: we shouldn't test fetching the leaderboard because the cookie only
# lasts 30 days and we only care about AoC in December. otherwise, we'd have
# to keep the cookie up to date just to pass tests.

def _names(members: List[Member]) -> List[str]:
    """Converts a list of members to a list of their names."""
    return [m.name for m in members]

def _tail(text: str) -> str:
    """Returns the last line from a string (split by newline character)."""
    return text.split('\n')[-1]

def _parse_members() -> List[Member]:
    """Returns a list of members from the test data."""
    return [Member.from_member_data(m, 2020)
            for m in ADVENT_TEST_DATA['members'].values()]

def test_advent_member_parse():
    """
    Tests parsing of the sample data.
    """
    members = _parse_members()

    assert len(members) == 26
    strayy = [m for m in members if m.name == 'Strayy'][0]

    assert strayy.name == 'Strayy'
    assert strayy.score == 24
    assert strayy.stars == 7
    # finished both parts, should have 2 times and a delta.
    assert strayy.day_times[1] == {1: 1297788, 2: 1298767}
    assert strayy.day_deltas[1] == 1298767 - 1297788
    # finished one part, should have 1 time and no delta.
    assert len(strayy.day_times[4]) == 1
    assert strayy.day_deltas[4] is None

def test_advent_member_sort_day():
    """
    Tests sorting by part 1, part 2, and delta times.
    """
    members = _parse_members()

    members.sort(key=Member.sort_key(SortMode.PART_1, 1))
    assert _names(members[:3]) == ['Cameron Aavik', 'rowboat1', 'kentonlam']

    members.sort(key=Member.sort_key(SortMode.PART_2, 1))
    assert _names(members[:3]) == ['Cameron Aavik', 'rowboat1', 'bradleysigma']

    members.sort(key=Member.sort_key(SortMode.DELTA, 1))
    assert _names(members[:3]) == \
        ['Matthew Low', 'Cameron Aavik', 'bradleysigma']

def test_advent_leaderboard_formats():
    """
    Tests very basic formatting of the leaderboard text.
    """
    members = _parse_members()
    jason = [m for m in members if m.name == 'Jason Hassell'][0]

    assert _tail(format_full_leaderboard([jason])) == \
        '  1)  282 ******.**..    *          Jason Hassell'
    assert _tail(format_day_leaderboard([jason], 1)) == \
        '  1)  0:50:48  0:53:04   0:02:16  Jason Hassell'

    matt = [m for m in members if m.name == 'Matthew Low'][0]
    assert _tail(format_day_leaderboard([matt], 16)) == \
        '  1)  0:45:03                     Matthew Low'

def test_advent_day_leaderboard_filters():
    """
    Day leaderboards should only contain users who have finished at least
    part 1.
    """
    members = _parse_members()

    assert 'Jason Hassell' not in format_advent_leaderboard(
        members, 17, SortMode.PART_2)

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
    members.sort(key=Member.sort_key(SortMode.SCORE))

    assert [member.name for member in members] == sorted_names
