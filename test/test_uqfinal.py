from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch

TEST_SEMESTER = {

}

TEST_COURSE = {
    "assessment": [
        {
            "weight": 10
        },
        {
            "weight": 15
        },
        {
            "weight": 15
        },
        {
            "weight": 60
        }
    ]
}


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
    assert(len(messages) == 2)
    assert(messages[1]["text"] == "Please choose a course")


@patch("uqcsbot.scripts.uqfinal.get_uqfinal_semesters", new=lambda: TEST_SEMESTER)
@patch("uqcsbot.scripts.uqfinal.get_uqfinal_course", new=get_uqfinal_course)
def test_invalid_course(uqcsbot: MockUQCSBot):
    """
    Test uqfinal when there is no course specified
    """
    invalid_course_name = "yeet"
    uqcsbot.post_message(TEST_CHANNEL_ID, f"!uqfinal {invalid_course_name}")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert(len(messages) == 2)
    assert(messages[1]["text"] ==
           f"Failed to retrieve course information for {invalid_course_name}")


@patch("uqcsbot.scripts.uqfinal.get_uqfinal_semesters", new=lambda: TEST_SEMESTER)
@patch("uqcsbot.scripts.uqfinal.get_uqfinal_course", new=get_uqfinal_course)
def test_successful(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!uqfinal CSSE2002 10 15 15")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert(len(messages) == 2)
    assert(messages[1]["text"].startswith("You need to achieve"))
