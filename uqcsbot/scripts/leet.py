from uqcsbot import bot, Command
from http import HTTPStatus
from uqcsbot.utils.command_utils import loading_status
import json
import requests
import random
from slackblocks import Attachment, SectionBlock
from typing import List, Tuple, Dict

LC_DIFFICULTY_MAP = ["easy", "medium", "hard"]  # leetcode difficulty is 1,2,3, need to map
HR_DS_API_LINK = ("https://www.hackerrank.com/rest/contests/master/tracks/" +
                  "data-structures/challenges?limit=200")
HR_ALG_API_LINK = ("https://www.hackerrank.com/rest/contests/master/tracks/" +
                   "algorithms/challenges?limit=200")
LC_API_LINK = 'https://leetcode.com/api/problems/all/'


COLORS = {"easy": "#5db85b",
          "medium": "#f1ad4e",
          "hard": "#d9534f"}


@bot.on_command('leet')
@loading_status
def handle_leet(command: Command) -> None:
    """
    `!leet [`easy` | `medium` | `hard`] - Retrieves a set of questions from online coding
    websites, and posts in channel with a random question from this set. If a difficulty
    is provided as an argument, the random question will be restricted to this level of
    challenge. Else, a random difficulty is generated to choose.
    """
    was_random = True  # Used for output later

    if command.has_arg():
        if (command.arg not in {"easy", "medium", "hard"}):
            bot.post_message(command.channel_id, "Usage: !leet [`easy` | `medium` | `hard`]")
            return
        else:
            difficulty = command.arg.lower()
            was_random = False
    else:
        difficulty = random.choice(LC_DIFFICULTY_MAP)  # No difficulty specified, randomly generate

    # List to store questions collected
    questions: List[Tuple[str, str]] = []

    # Go fetch questions from APIs
    collect_questions(questions, difficulty)
    selected_question = select_question(questions)  # Get a random question

    # If we didn't find any questions for this difficulty, try again, probably timeout on all 3
    if (selected_question is None):
        bot.post_message(command.channel_id,
                         "Hmm, the internet pipes are blocked. Try that one again.")
        return

    # Leetcode difficulty colors
    color = COLORS[difficulty]

    if (was_random):
        title_text = f"Random {difficulty} question generated!"
    else:
        # Style this a bit nicer
        difficulty = difficulty.title()
        title_text = f"{difficulty} question generated!"

    difficulty = difficulty.title()  # If we haven't already (i.e. random question)

    msg_text = f"Here's a new question for you! <{selected_question[1]}|{selected_question[0]}>"

    bot.post_message(command.channel_id, text=title_text,
                     attachments=[Attachment(SectionBlock(msg_text), color=color)._resolve()])


def select_question(questions: list) -> Tuple[str, str]:
    """
    Small helper method that selects a question from a list randomly
    """
    if (len(questions) == 0):
        return None
    return random.choice(questions)


def collect_questions(questions: List[str], difficulty: str):
    """
    Helper method to send GET requests to various Leetcode and HackerRank APIs.
    Populates provided dict (urls) with any successfully retrieved data,
    in the form of (Question_Title, Question_Link) tuple pairs.
    """
    options = [("Hackerrank data structure", HR_DS_API_LINK),
               ("Hackerrank Algorithms structure", HR_ALG_API_LINK),
               ("Leetcode", LC_API_LINK),
               ]

    results = []

    # Get all the questions off the internet: hr data struct, hr algo, all leetcode
    for name, url in options:
        try:
            results.append((name, requests.get(url, timeout=3)))
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout) as error:
            print(name + " API timed out!" + "\n" + str(error))
            results.append((name, None))

    json_blobs: Dict[str, List[Dict]] = {}

    for name, response in results:
        if (response is None or response.status_code != HTTPStatus.OK):
            if (name != "Leetcode"):
                json_blobs["parsed_hr_all"] = json_blobs.get("parsed_hr_all", []) + []
            else:
                json_blobs["parsed_lc_all"] = []
        else:
            if (name != "Leetcode"):
                parsed_hr_data = json.loads(response.text)
                json_blobs["parsed_hr_all"] = (json_blobs.get("parsed_hr_all", []) +
                                               parsed_hr_data["models"])
            else:
                parsed_lc_data = json.loads(response.text)
                json_blobs["parsed_lc_all"] = parsed_lc_data["stat_status_pairs"]

    # Build HackerRank questions tuples from data
    for question in json_blobs["parsed_hr_all"]:
        # Construct a tuple pair of title for formatting and link to question
        question_data = (question["name"], "http://hackerrank.com/challenges/" + question["slug"]
                         + "/problem")
        question_difficulty = question["difficulty_name"].lower()

        # HackerRank annoyingly has 5 difficulty levels, anything above hard is hard
        if (question_difficulty == "advanced" or question_difficulty == "expert"):
            question_difficulty = "hard"

        if (question_difficulty == difficulty):
            questions.append(question_data)

    # Build leetcode question tuples from data, but only the free ones
    for question in json_blobs["parsed_lc_all"]:
        if (question["paid_only"] is False):
            question_data = (question["stat"]["question__title"], "https://leetcode.com/problems/"
                             + question["stat"]["question__title_slug"] + "/")

            question_difficulty = LC_DIFFICULTY_MAP[question["difficulty"]["level"] - 1]

            if (question_difficulty == difficulty):
                questions.append(question_data)
