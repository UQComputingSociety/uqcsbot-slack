import argparse
import requests
import json
import base64
import random
from typing import List
from uqcsbot import bot, Command
from uqcsbot.api import Channel
from uqcsbot.utils.command_utils import loading_status, UsageSyntaxException

API_URL = "https://opentdb.com/api.php"
CATEGORIES_URL = "https://opentdb.com/api_category.php"

MAX_SECONDS = 300

# Customisation options
BOOLEAN_REACTS = ['this', 'not-this']
MULTIPLE_CHOICE_REACTS = ['green_heart', 'yellow_heart', 'heart', 'blue_heart']
CHOICE_COLORS = ['#6C9935', '#F3C200', '#B6281E', '#3176EF']

@bot.on_command('trivia')
@loading_status
def handle_trivia(command: Command):
    """
        `!trivia [-d <easy|medium|hard>] [-c <CATEGORY>] [-t <mult|tf>] [-s <N>] [--cats]` - Asks a new trivia question
    """

    args = parse_arguments(command)

    # TODO: Should the help be sent to the channel or just the user?
    # End early if the help option was used
    if args.help:
        return


    # Send the possible categories
    if args.cats:
        bot.post_message(command.channel_id, get_categories())
        return

    handle_question(command, args)

    schedule_answer(command, args.seconds)


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
                        help='The difficulty of the question. (default: %(default)s')
    parser.add_argument('-c', '--category', default=-1, type=int, help='Specifies a category (default: any)')
    parser.add_argument('-t', '--type', choices={"tf": "boolean", "mult": "multiple"}, default="random", type=str.lower,
                        help='The type of question. (default: %(default)s)')
    parser.add_argument('-s', '--seconds', default=30, type=int,
                        help='Number of seconds before posting answer (default: %(default)s')
    parser.add_argument('--cats', action='store_true', help='Sends a list of valid categories to the user')
    parser.add_argument('-h', '--help', action='store_true')

    args = parser.parse_args(command_args)

    # If the help option was used print the help message to the channel (needs access to the parser to do this)
    if args.help:
        bot.post_message(command.channel_id, parser.format_help())

    # Constrain the number of seconds to a reasonable frame
    args.seconds = max(0, args.seconds)
    args.seconds = min(args.seconds, MAX_SECONDS)

    return args

def get_categories() -> str:
    """
    Gets the message to send if the user wants a list of the available categories
    """
    http_response = requests.get(CATEGORIES_URL)
    if http_response.status_code != requests.codes.ok:
        return "There was a problem getting the response"

    categories = json.loads(http_response.content)['trivia_categories']

    # Construct pretty results to print in a code block to avoid a large spammy message
    pretty_results = '```Use the id to specify a specific category \n\nID  Name\n'

    for category in categories:
        id = category['id']
        name = category['name']
        pretty_results += f'{id:<4d}{name}\n'

    pretty_results += '```'

    return pretty_results

def decode_b64(input: str) -> str:
    """
    Takes a base64 encoded string. Returns the decoded version to utf-8.
    """
    return base64.b64decode(input).decode('utf-8')

def handle_question(command: Command, args: argparse.Namespace):
    params = {'amount': 1, 'encode': 'base64'}

    # Add in any explicitly specified arguments
    if args.category != -1:
        params['category'] = args.category

    if args.difficulty != 'random':
        params['difficulty'] = args.difficulty

    if args.type != 'random':
        params['type'] = 'boolean' if args.type == 'tf' else 'multiple'

    http_response = requests.get(API_URL, params=params)
    if http_response.status_code != requests.codes.ok:
        return "There was a problem getting the response"

    response_content = json.loads(http_response.content)
    if response_content['response_code'] == 2:
        return "Invalid category id. Try !trivia --cats for a list of valid categories."
    elif response_content['response_code'] != 0:
        return "No results were returned"

    question_data = response_content['results'][0]

    # The base 64 decoding ensures that the formatting works properly with slack
    question = decode_b64(question_data["question"])
    correct_answer = decode_b64(question_data["correct_answer"])
    answers = [decode_b64(ans) for ans in question_data["incorrect_answers"]]

    # Whether or not the question was a true/false question
    is_boolean = len(answers) == 1

    # Post the question and get the timestamp for the reactions (asterisks bold it)
    message_ts = bot.post_message(command.channel_id, f'*{question}*')['ts']


    # Print the questions (if multiple choice) and add the answer reactions
    reactions = []
    if is_boolean:
        reactions = BOOLEAN_REACTS
    else:
        reactions = MULTIPLE_CHOICE_REACTS

        answers.append(correct_answer)
        message_ts = post_possible_answers(command.channel_id, answers)

    for reaction in reactions:
        bot.api.reactions.add(name=reaction, channel=command.channel_id, timestamp=message_ts)

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

def schedule_answer(command: Command, secs: int):
    pass