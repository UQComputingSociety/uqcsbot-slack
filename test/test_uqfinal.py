from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch
from typing import Dict, Any

TEST_SEMESTER: Dict[str, Any] = {}

TEST_COURSE = {"assessment": [{'taskName': 'Assignment 1', "weight": 10},
                              {'taskName': 'Assignment 2', "weight": 15},
                              {'taskName': 'Assignment 3', "weight": 15},
                              {'taskName': 'Final examination', "weight": 60}]}


def get_uqfinal_course(semester, course: str):
    if course.lower() == "csse2002":
        return TEST_COURSE
    else:
        return None


def test_no_course(uqcsbot: MockUQCSBot):
    """
    Test uqfinal when there is no course specified
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!uqfinal")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[1]["text"] == "Please choose a course"


@patch("uqcsbot.scripts.uqfinal.get_uqfinal_semesters", new=lambda: TEST_SEMESTER)
@patch("uqcsbot.scripts.uqfinal.get_uqfinal_course", new=get_uqfinal_course)
def test_invalid_course(uqcsbot: MockUQCSBot):
    """
    Test uqfinal when there is no course specified
    """
    invalid_course_name = "yeet"
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!uqfinal {invalid_course_name}")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert (messages[1]["text"] ==
            f"Failed to retrieve course information for {invalid_course_name}")


@patch("uqcsbot.scripts.uqfinal.get_uqfinal_semesters", new=lambda: TEST_SEMESTER)
@patch("uqcsbot.scripts.uqfinal.get_uqfinal_course", new=get_uqfinal_course)
def test_final(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!uqfinal CSSE2002 10% 15 0.15")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 3
    assert (messages[-2]["text"] ==
            "Inputted score of 10% for Assignment 1 (weighted 10%)\n"
            "Inputted score of 15% for Assignment 2 (weighted 15%)\n"
            "Inputted score of 15% for Assignment 3 (weighted 15%)")
    assert (messages[-1]["text"] ==
            "You need to score at least 75% on the Final examination to achieve a four.\n"
            "You need to score at least 100% on the Final examination to achieve a five.\n"
            "_Disclaimer: this does not take hurdles into account._\n"
            "_Powered by http://uqfinal.com_")


@patch("uqcsbot.scripts.uqfinal.get_uqfinal_semesters", new=lambda: TEST_SEMESTER)
@patch("uqcsbot.scripts.uqfinal.get_uqfinal_course", new=get_uqfinal_course)
def test_partial(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!uqfinal CSSE2002 50% 50%")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 3
    assert (messages[-2]["text"] ==
            "Inputted score of 50% for Assignment 1 (weighted 10%)\n"
            "Inputted score of 50% for Assignment 2 (weighted 15%)")
    assert (messages[-1]["text"] ==
            "You need to score at least a weighted average of 50% on the"
            " remaining 2 assessments to achieve a four.\n"
            "You need to score at least a weighted average of 70% on the"
            " remaining 2 assessments to achieve a five.\n"
            "You need to score at least a weighted average of 84% on the"
            " remaining 2 assessments to achieve a six.\n"
            "You need to score at least a weighted average of 97% on the"
            " remaining 2 assessments to achieve a seven.\n"
            "_Disclaimer: this does not take hurdles into account._\n"
            "_Powered by http://uqfinal.com_")


@patch("uqcsbot.scripts.uqfinal.get_uqfinal_semesters", new=lambda: TEST_SEMESTER)
@patch("uqcsbot.scripts.uqfinal.get_uqfinal_course", new=get_uqfinal_course)
def test_list(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!uqfinal CSSE2002")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert (messages[-1]["text"] ==
            "CSSE2002 has the following assessments:\n"
            "1: Assignment 1 (10%)\n"
            "2: Assignment 2 (15%)\n"
            "3: Assignment 3 (15%)\n"
            "4: Final examination (60%)\n"
            "_Powered by http://uqfinal.com_")


@patch("uqcsbot.scripts.uqfinal.get_uqfinal_semesters", new=lambda: TEST_SEMESTER)
@patch("uqcsbot.scripts.uqfinal.get_uqfinal_course", new=get_uqfinal_course)
def test_bad_number(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!uqfinal CSSE2002 asdf")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert (messages[-1]["text"] == "\"asdf\" could not be converted to a number.")


@patch("uqcsbot.scripts.uqfinal.get_uqfinal_semesters", new=lambda: TEST_SEMESTER)
@patch("uqcsbot.scripts.uqfinal.get_uqfinal_course", new=get_uqfinal_course)
def test_bad_range(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!uqfinal CSSE2002 120%")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert (messages[-1]["text"] == "Assessments scores should be between 0% and 100%.")


@patch("uqcsbot.scripts.uqfinal.get_uqfinal_semesters", new=lambda: TEST_SEMESTER)
@patch("uqcsbot.scripts.uqfinal.get_uqfinal_course", new=get_uqfinal_course)
def test_bad_count(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!uqfinal CSSE2002 2 4 6 8 10")
    # Five! Five Pieces of Assessment! Ha! Ha! Ha!
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert (messages[-1]["text"] ==
            "Too many retults provided.\n"
            "This course has 4 assessments.")
