import json
from typing import List
from uqcsbot.utils.command_utils import UsageSyntaxException
from uqcsbot.scripts.advent import (Member, SortMode, format_advent_leaderboard,
                                    format_day_leaderboard, format_full_leaderboard,
                                    format_global_leaderboard, parse_arguments)

from pytest import raises

with open("./test/advent_test_data.json", encoding="utf-8") as f:
    ADVENT_TEST_DATA = json.load(f)

# remark: we shouldn't test fetching the leaderboard because the cookie only
# lasts 30 days and we only care about AoC in December. otherwise, we'd have
# to keep the cookie up to date just to pass tests.

def _names(members: List[Member]) -> List[str]:
    """Converts a list of members to a list of their names."""
    return [m.name for m in members]

def _tail(text: str) -> str:
    """Returns the last line from a string (split by newline character)."""
    return text.split("\n")[-1]

def _parse_members(day=None) -> List[Member]:
    """Returns a list of members from the test data."""
    return [Member.from_member_data(m, 2020, day) for m in ADVENT_TEST_DATA["members"].values()]

def _member(name: str, day=None) -> Member:
    """Returns the member with the given name and data on the given day."""
    return min(m for m in _parse_members(day) if m.name == name)

def test_advent_member_parse():
    """
    Tests parsing of the sample data.
    """
    members = _parse_members()

    assert len(members) == 26
    strayy, = (m for m in members if m.name == "Strayy")

    assert strayy.name == "Strayy"
    assert strayy.local == 24
    assert strayy.stars == 7
    # finished both parts, should have 2 times and a delta.
    assert strayy.all_times[1] == {1: 1297788, 2: 1298767}
    assert strayy.all_deltas[1] == 1298767 - 1297788
    # finished one part, should have 1 time and no delta.
    assert len(strayy.all_times[4]) == 1
    assert strayy.all_deltas[4] is None

def test_advent_member_sort_day():
    """
    Tests sorting by part 1, part 2, and delta times.
    """
    members = _parse_members(1)

    members.sort(key=Member.sort_key(SortMode.PART_1))
    assert _names(members[:3]) == ["Cameron Aavik", "rowboat1", "kentonlam"]

    members.sort(key=Member.sort_key(SortMode.PART_2))
    assert _names(members[:3]) == ["Cameron Aavik", "rowboat1", "bradleysigma"]

    members.sort(key=Member.sort_key(SortMode.DELTA))
    assert _names(members[:3]) == ["Matthew Low", "Cameron Aavik", "bradleysigma"]

def test_advent_leaderboard_formats():
    """
    Tests very basic formatting of the leaderboard text.
    """
    jason = _member("Jason Hassell", 1)
    assert (_tail(format_full_leaderboard([jason]))
            == "  1)  282 ******.**..    *          Jason Hassell")
    assert (_tail(format_day_leaderboard([jason]))
            == "  1)  0:50:48  0:53:04   0:02:16  Jason Hassell")

    matt = _member("Matthew Low", 16)
    assert (_tail(format_day_leaderboard([matt]))
            == "  1)  0:45:03                     Matthew Low")

    hines = _member("Thomas Hines")
    assert (_tail(format_global_leaderboard([hines]))
            == "  1)   66 Thomas Hines")

def test_advent_day_leaderboard_filters():
    """
    Day leaderboards should only contain users who have finished at least
    part 1.
    """
    members = _parse_members(17)

    assert "Jason Hassell" not in format_advent_leaderboard(members, True, False, SortMode.PART_2)

def test_advent_arguments():
    """
    Tests argument parsing of !advent. Mostly just --sort
    """

    with raises(UsageSyntaxException):
        parse_arguments(["-y", "2020", "--help"])

    args = parse_arguments(["-y", "2019", "20", "-c", "1001"])
    assert args.year == 2019
    assert args.day == 20
    assert args.code == 1001

    assert parse_arguments(["-s", "p1"]).sort == SortMode.PART_1
    assert parse_arguments(["-s", "p2"]).sort == SortMode.PART_2
    assert parse_arguments(["-s", "delta"]).sort == SortMode.DELTA

    for invalid in ("borg", "score", "s", "1", "2"):
        with raises(UsageSyntaxException):
            parse_arguments(["-s", invalid])

def test_advent_member_sort():
    """
    Tests that the comparator function on Member is sane
    """
    sorted_names = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot"]

    members = [Member("delta", 20, 10, 3),
               Member("bravo", 20, 20, 4),
               Member("alpha", 30, 30, 6),
               Member("foxtrot", 10, 10, 2),
               Member("charlie", 20, 20, 4),
               Member("echo", 10, 40, 5)]
    members.sort(key=Member.sort_key(SortMode.LOCAL))

    assert [member.name for member in members] == sorted_names
