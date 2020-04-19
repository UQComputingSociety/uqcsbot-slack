from uqcsbot import bot, Command
from http import HTTPStatus
from uqcsbot.utils.command_utils import loading_status, UsageSyntaxException
import json
import requests
import random
from slackblocks import Attachment, SectionBlock


LC_DIFFICULTY_MAP = ["easy", "medium", "hard"] # leetcode difficulty is 1,2,3, need to map
HR_DS_API_LINK = ("https://www.hackerrank.com/rest/contests/master/tracks/" +
    "data-structures/challenges?limit=200")
HR_ALG_API_LINK = "https://www.hackerrank.com/rest/contests/master/tracks/algorithms/challenges?limit=200"
LC_API_LINK = 'https://leetcode.com/api/problems/all/'

EASY_COLOR_CODE = "#5db85b"
MED_COLOR_CODE = "#f1ad4e"
HARD_COLOR_CODE = "#d9534f"

@bot.on_command('leet')
@loading_status
def handle_leet(command: Command) -> None:
    """
    `!leet [`easy` | `medium` | `hard`] - Retrieves a set of questions from online coding
    websites, and posts in channel with a random question from this set. If a difficulty
    is provided as an argument, the random question will be restricted to this level of 
    challenge. Else, a random difficulty is generated to choose.
    """

    difficulty = ""
    wasRandom = True # Used for output later

    if command.has_arg():
        if (command.arg not in {"easy", "medium", "hard"}):
           bot.post_message(command.channel_id, "Usage: !leet [`easy` | `medium` | `hard`]")
           return
        else:
            difficulty = command.arg.lower()
            wasRandom = False

    # Storage dict for the three categories, difficulty is key
    questions = {"hard" : [], "medium" : [], "easy" : []}

    # Go fetch questions from APIs
    collect_questions(questions)

    # No difficulty specified, randomly generate one
    if (len(difficulty) == 0):
        difficulty = random.choice(LC_DIFFICULTY_MAP) 
    
    
    selected_question = select_question(difficulty, questions) # Get a random question

    # If we didn't find any questions for this difficulty, try again, probably timeout on all 3
    if (len(selected_question) == 0):
        bot.post_message(command.channel_id, 
            "Hmm, the internet pipes are blocked. Try that one again.")
        return

    # Leetcode difficulty colors
    if (difficulty == "easy"):
        color = EASY_COLOR_CODE # Could make these constants, but they're just ripped from LC
    elif (difficulty == "medium"):
        color = MED_COLOR_CODE
    else:
        color = HARD_COLOR_CODE

    

    if (wasRandom):
        title_text = f"Random {difficulty} question generated!"
    else:
        # Style this a bit nicer
        difficulty = difficulty.title()
        title_text = f"{difficulty} question generated!"
    
    difficulty = difficulty.title() # If we haven't already (i.e. random question)

    msg_text = f"Here's a new question for you! <{selected_question[1]}|{selected_question[0]}>"

    bot.post_message(command.channel_id, text=title_text,
                    attachments=[Attachment(SectionBlock(msg_text), color=color)._resolve()])



def select_question(difficulty, questions):
    if (len(questions[difficulty]) == 0):
        return ()
    return random.choice(questions[difficulty])


def collect_questions(questions):
    """
    Helper method to send GET requests to various Leetcode and HackerRank APIs. 
    Populates provided dict (urls) with any successfully retrieved data, 
    in the form of (Question_Title, Question_Link) tuple pairs.
    """

    # Get all the questions off the internet: hr data struct, hr algo, all leetcode
    try: 
        hr_ds = requests.get(HR_DS_API_LINK, headers={'User-Agent': 'Mozilla/5.0'}, 
            timeout = 3)
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout) as error:
        print("HackerRank Data Structure API timed out!" + "\n" + str(error))
        hr_ds = None # If any of these fail (timeout etc) make them None for catching later

    try:
        hr_alg = requests.get(HR_ALG_API_LINK, headers={'User-Agent': 'Mozilla/5.0'}, timeout = 3)
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout) as error:
        print("Hackerrank Algorithms API timed out!" + "\n" + str(error))
        hr_alg = None

    try:
        lc_all = requests.get(LC_API_LINK, timeout=3)
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout) as error:
        print("Leetcode API timed out!" + "\n" + str(error))
        lc_all = None
    
    
    # Parse the JSON blobs grabbed; if bad response, make dummy values to not include
    if (hr_ds == None or hr_ds.status_code != HTTPStatus.OK):
            parsed_hr_ds = {"models" : []} # just make an empty list
    else:
        parsed_hr_ds = json.loads(hr_ds.text)
        
    if (hr_alg == None or hr_alg.status_code != HTTPStatus.OK):
        parsed_hr_alg = {"models" : []} # same as above, if no response just ignore
    else:
        parsed_hr_alg = json.loads(hr_alg.text)

    if (lc_all == None or lc_all.status_code != HTTPStatus.OK):
        parsed_lc_all = {"stat_status_pairs": []} 
    else:
        parsed_lc_all = (json.loads(lc_all.text))

    
    # Combine the two HackerRank json blobs as they have same structure (models has data)
    parsed_hr_all = parsed_hr_alg["models"] + parsed_hr_ds["models"]

    # Build HackerRank questions tuples from data
    for question in parsed_hr_all:
        # Construct a tuple pair of title for formatting and link to question
        question_data = (question["name"], "http://hackerrank.com/challenges/" + question["slug"]
            + "/problem")
        question_difficulty = question["difficulty_name"].lower()

        # HackerRank annoyingly has 5 difficulty levels, anything above hard is hard
        if (question_difficulty == "advanced" or question_difficulty == "expert"):
            question_difficulty = "hard"
        
        questions[question_difficulty].append(question_data)
    
    # Build leetcode question tuples from data, but only the free ones
    for question in parsed_lc_all["stat_status_pairs"]:
        if (question["paid_only"] == False):
            question_data = (question["stat"]["question__title"], "https://leetcode.com/problems/"
                + question["stat"]["question__title_slug"] + "/")

            questions[LC_DIFFICULTY_MAP[question["difficulty"]["level"] - 1]].append(question_data)
    







