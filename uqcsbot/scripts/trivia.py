import argparse
import base64
import json
import random
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Union, NamedTuple

from uqcsbot import bot, Command
from uqcsbot.api import Channel
from uqcsbot.utils.command_utils import loading_status, UsageSyntaxException

API_URL = "https://opentdb.com/api.php"
CATEGORIES_URL = "https://opentdb.com/api_category.php"

# NamedTuple for use with the data returned from the api
QuestionData = NamedTuple('QuestionData',
                          [('type', str), ('question', str), ('correct_answer', str), ('incorrect_answers', List[str])])

# Customisation options
MIN_SECONDS = 5
MAX_SECONDS = 300

BOOLEAN_REACTS = ['this', 'not-this']  # Format of [ <True>, <False> ]
MULTIPLE_CHOICE_REACTS = ['green_heart', 'yellow_heart', 'heart', 'blue_heart']
CHOICE_COLORS = ['#6C9935', '#F3C200', '#B6281E', '#3176EF']


@bot.on_command('trivia')
@loading_status
def handle_trivia(command: Command):
    """
        `!trivia [-d <easy|medium|hard>] [-c <CATEGORY>] [-t <multiple|tf>] [-s <N>] [--cats]`
            - Asks a new trivia question
    """
    args = parse_arguments(command)

    # End early if the help option was used
    if args.help:
        return

    # Send the possible categories
    if args.cats:
        bot.post_message(command.channel_id, get_categories())
        return

    handle_question(command, args)


def parse_arguments(command: Command) -> argparse.Namespace:
    """
    Parses the arguments for the command
    :param command: The command which the handle_trivia function receives
    :return: An argpase Namespace object with the parsed arguments
    """
    command_args = command.arg.split() if command.has_arg() else []

    parser = argparse.ArgumentParser(prog='!trivia', add_help=False)

    def usage_error(*args, **kwargs):
        raise UsageSyntaxException()

    parser.error = usage_error  # type: ignore
    parser.add_argument('-d', '--difficulty', choices=['easy', 'medium', 'hard'], default='random', type=str.lower,
                        help='The difficulty of the question. (default: %(default)s)')
    parser.add_argument('-c', '--category', default=-1, type=int, help='Specifies a category (default: any)')
    parser.add_argument('-t', '--type', choices=['boolean', 'multiple'], default="random", type=str.lower,
                        help='The type of question. (default: %(default)s)')
    parser.add_argument('-s', '--seconds', default=30, type=int,
                        help='Number of seconds before posting answer (default: %(default)s)')
    parser.add_argument('--cats', action='store_true', help='Sends a list of valid categories to the user')
    parser.add_argument('-h', '--help', action='store_true')

    args = parser.parse_args(command_args)

    # If the help option was used print the help message to the channel (needs access to the parser to do this)
    if args.help:
        bot.post_message(command.channel_id, parser.format_help())

    # Constrain the number of seconds to a reasonable frame
    args.seconds = max(MIN_SECONDS, args.seconds)
    args.seconds = min(args.seconds, MAX_SECONDS)

    return args


def get_categories() -> str:
    """Gets the message to send if the user wants a list of the available categories."""
    http_response = requests.get(CATEGORIES_URL)
    if http_response.status_code != requests.codes.ok:
        return "There was a problem getting the response"

    categories = json.loads(http_response.content)['trivia_categories']

    # Construct pretty results to print in a code block to avoid a large spammy message
    pretty_results = '```Use the id to specify a specific category \n\nID  Name\n'

    for category in categories:
        pretty_results += f'{category["id"]:<4d}{category["name"]}\n'

    pretty_results += '```'

    return pretty_results


def handle_question(command: Command, args: argparse.Namespace):
    """Handles getting a question and posting it to the channel as well as scheduling the answer"""
    question_data = get_question_data(command.channel_id, args)

    if question_data is None:
        return

    # The base 64 decoding ensures that the formatting works properly with slack
    question = decode_b64(question_data.question)
    correct_answer = decode_b64(question_data.correct_answer)
    answers = [decode_b64(ans) for ans in question_data.incorrect_answers]

    # Whether or not the question was a true/false question
    is_boolean = len(answers) == 1

    # Post the question and get the timestamp for the reactions (asterisks bold it)
    message_ts = bot.post_message(command.channel_id, f'*{question}*')['ts']

    # Print the questions (if multiple choice) and add the answer reactions
    if is_boolean:
        reactions = BOOLEAN_REACTS
        answer_text = f':{BOOLEAN_REACTS[0]}:' if correct_answer == 'True' else f':{BOOLEAN_REACTS[1]}:'
    else:
        reactions = MULTIPLE_CHOICE_REACTS
        answer_text = correct_answer

        answers.append(correct_answer)
        message_ts = post_possible_answers(command.channel_id, answers)

    for reaction in reactions:
        bot.api.reactions.add(name=reaction, channel=command.channel_id, timestamp=message_ts)

    # Schedule the answer to be posted after the specified number of seconds has passed
    answer_message = f'*The answer is: {answer_text}*'
    schedule_answer(command, answer_message, args.seconds)


def get_question_data(channel: Channel, args: argparse.Namespace) -> QuestionData:
    """
    Attempts to get a question from teh api using the specified arguments.
    Returns the dictionary object for the question on success and None on failure (after posting an error message).
    """
    # Base64 to help with encoding the message for slack
    params: Dict[str, Union[int, str]] = {'amount': 1, 'encode': 'base64'}

    # Add in any explicitly specified arguments
    if args.category != -1:
        params['category'] = args.category

    if args.difficulty != 'random':
        params['difficulty'] = args.difficulty

    if args.type != 'random':
        params['type'] = args.type

    # Get the response and check that it is valid
    http_response = requests.get(API_URL, params=params)
    if http_response.status_code != requests.codes.ok:
        bot.post_message(channel, "There was a problem getting the response")
        return None

    # Check the response codes and post a useful message in the case of an error
    response_content = json.loads(http_response.content)
    if response_content['response_code'] == 2:
        bot.post_message(channel, "Invalid category id. Try !trivia --cats for a list of valid categories.")
        return None
    elif response_content['response_code'] != 0:
        bot.post_message(channel, "No results were returned")
        return None

    question_data = response_content['results'][0]

    # Delete the ones we don't need
    del question_data['category']
    del question_data['difficulty']

    return QuestionData(**question_data)


def decode_b64(encoded: str) -> str:
    """Takes a base64 encoded string. Returns the decoded version to utf-8."""
    return base64.b64decode(encoded).decode('utf-8')


def post_possible_answers(channel: Channel, answers: List[str]) -> float:
    """
    Posts the possible answers for a multiple choice question in a nice way.
    Returns the timestamp of the message to allow reacting to it.
    """
    random.shuffle(answers)

    attachments = []
    for col, answer in zip(CHOICE_COLORS, answers):
        ans_att = {'text': answer, 'color': col}
        attachments.append(ans_att)

    return bot.post_message(channel, '', attachments=attachments)['ts']


def schedule_answer(command: Command, answer: str, secs: int):
    """Schedules the given answer to be posted to the channel after the given number of seconds"""
    post_answer = lambda: bot.post_message(command.channel_id, answer)
    end_date = datetime.now(timezone(timedelta(hours=10))) + timedelta(seconds=secs + 1)

    bot._scheduler.add_job(post_answer, 'interval', seconds=secs, end_date=end_date)
