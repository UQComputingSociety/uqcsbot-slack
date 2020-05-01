from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
import json
from unittest.mock import patch


LC_DIFFICULTY_MAP = ["easy", "medium", "hard"]


def mocked_api_request(questions, difficulty):
    # Loads local json file from lc to populate a dict
    with open('test/leetcode.json', "rb") as question_bank:
        lc_data = json.load(question_bank)
        for question in lc_data["stat_status_pairs"]:
            if (question["paid_only"] is False):
                lc_data = (question["stat"]["question__title"], "https://leetcode.com/problems/"
                           + question["stat"]["question__title_slug"] + "/")

                question_difficulty = LC_DIFFICULTY_MAP[question["difficulty"]["level"] - 1]

                if (question_difficulty == difficulty):
                    questions.append(lc_data)


def mocked_empty_api_call(questions, difficulty):
    return questions


def mocked_easy_only(questions, difficulty):
    questions.append(("Test Question", "https://www.google.com"))


@patch("uqcsbot.scripts.leet.collect_questions", new=mocked_api_request)
def test_api_call(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, '!leet')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert (len(messages) == 2)


@patch("uqcsbot.scripts.leet.collect_questions", new=mocked_empty_api_call)
def test_empty_api_call(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, '!leet')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert (messages[1]['text'] == "Hmm, the internet pipes are blocked. Try that one again.")


def test_bad_difficulty(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, '!leet dkjfsh')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert (messages[1]['text'] == "Usage: !leet [`easy` | `medium` | `hard`]")


@patch("uqcsbot.scripts.leet.collect_questions", new=mocked_easy_only)
def test_specific_difficulty(uqcsbot: MockUQCSBot):
    uqcsbot.post_message(TEST_CHANNEL_ID, '!leet easy')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])

    assert (messages[1]['text'] == "Easy question generated!")
    assert (messages[1]['attachments'][0]['blocks'][0]['text']['text'] == "Here's a new question "
            + "for you! <https://www.google.com|Test Question>")
