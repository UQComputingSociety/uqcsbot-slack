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

def test_no_course(uqcsbot: MockUQCSBot):
    """
    Test uqfinal when there is no course specified
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, "!uqfinal")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert(len(messages) == 2)
    assert(messages[1]["text"] == "Please choose a course")

    
@patch("uqcsbot.scripts.uqfinal.get_uqfinal_semesters", new=lambda: TEST_SEMESTER)
@patch("uqcsbot.scripts.uqfinal.get_uqfinal_course", new=lambda a, b: TEST_COURSE)
def test_successful(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, "!uqfinal CSSE2002 10 15 15")
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert(len(messages) == 2)
    assert(messages[1]["text"].startswith("You need to achieve"))