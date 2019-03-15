import argparse
import json
from typing import NamedTuple, Union, Optional, List, Dict, Tuple

import requests

from uqcsbot import bot, Command
from uqcsbot.api import Channel
from uqcsbot.utils.command_utils import loading_status, UsageSyntaxException

BASE_URL = "https://crates.io/api/v1"
MAX_LIMIT = 15  # The maximum number of search results from one call to the command

# NamedTuple for the case that the argparse finds a -h flag
HelpCommand = NamedTuple('HelpCommand', [('help_string', str)])

# NamedTuple for the default command that deals with searching for specific crates
CrateSearch = NamedTuple('CrateSearch',
                         [('name', str), ('limit', int), ('category', str), ('user', str), ('sort', str),
                          ('search', str)])

# NamedTuple for the default categories sub-command that deals with searching for categories
CategorySearch = NamedTuple('CategorySearch', [('name', str), ('limit', int), ('sort', str)])

# Named tuple for a crate that was found in a search
CrateResult = NamedTuple('CrateResult', [('name', str), ('downloads', int), ('homepage', str), ('description', str)])

@bot.on_command('crates')
@loading_status
def handle_crates(command: Command):
    """
    `!crates `
            - Get information about crates from crates.io
    """
    args = parse_arguments(command.channel_id, command.arg if command.has_arg() else '')

    args.execute_action(command.channel_id, args)  # type: ignore


def parse_arguments(channel: Channel, arg_str: str) -> Union[HelpCommand, CrateSearch, CategorySearch]:
    """
    Parses the arguments passed to the command
    :param channel: The channel to post help to (help message needs access to parser)
    :param arg_str: The argument string (not including "!crates")
    """
    parser = argparse.ArgumentParser(prog="!crates", add_help=False)
    subparsers = parser.add_subparsers()

    # Change the parsers default on error behaviour
    def usage_error(*args, **kwargs):
        raise UsageSyntaxException()

    parser.error = usage_error  # type: ignore

    # Converts "Date and time" into "date-and-time" which is the format used for category ids
    category_formatter = lambda id: id.lower().strip().replace(' ', '-')
    search_limit = lambda val: max(1, min(int(val), MAX_LIMIT))  # limits the val such that 0 < val <= MaxLimit

    # For "!crates {args}"
    parser.add_argument('-h', '--help', action='store_true', help='Prints this help message')
    query_group = parser.add_mutually_exclusive_group(required=False)
    query_group.add_argument('-n', '--name', default='', type=str.lower,
                             help="The name of the crate to get information about")
    query_group.add_argument('-s', '--search', default='', type=str.lower,
                             help='Search for a crate instead of using its exact name')
    parser.add_argument('-l', '--limit', default=5, type=search_limit,
                        help='When not searching for a specific crate how many results should be shown? '
                             '(max: ' + str(MAX_LIMIT) + ', default: %(default)s)')
    parser.add_argument('-c', '--category', default='', type=category_formatter,
                        help="Limit results to crates in this category")
    parser.add_argument('-u', '--user', default='', type=str, help='Limit results by crate author')
    parser.add_argument('-o', '--sort', choices=['alpha', 'downloads'], default='downloads', type=str.lower,
                        help='Sort the results by alphabetical order or by number of downloads (default: %(default)s)')
    parser.set_defaults(execute_action=handle_crates_route, crates_route=True)

    # For "!crates categories {args}"
    category_parser = subparsers.add_parser('categories', add_help=False,
                                            help='Sub-command to get information about categories instead of crates')
    category_parser.add_argument('-h', '--help', action='store_true', help='Prints this help message')
    category_parser.add_argument('-n', '--name', default='', type=category_formatter,
                                 help='Specify a specific category to get more information about it')
    category_parser.add_argument('-l', '--limit', default=5, type=search_limit,
                                 help=f'When not searching for a specific category how many results should be shown? '
                                      '(max:  ' + str(MAX_LIMIT) + ', default: %(default)s)')
    category_parser.add_argument('-s', '--sort', choices=['alpha', 'crates'], default='alpha', type=str.lower,
                                 help='Sort the result by alphabetical order or by number of crates in the category')
    category_parser.set_defaults(execute_action=handle_categories_route, crates_route=False)

    # TODO: For "!crates users {args}"

    args = parser.parse_args(arg_str.split())

    # If the arguments show that help was requested then change the execute_action and add the help string
    if args.help:
        args.execute_action = handle_help_route
        if args.crates_route:
            args.help_string = parser.format_help()
        else:
            args.help_string = category_parser.format_help()

    return args


def handle_help_route(channel: Channel, args: HelpCommand):
    "This is called whenever the -h argument is invoked regardless of sub-command."
    bot.post_message(channel, args.help_string)


def get_user_id(username: str) -> int:
    "Tries to get the users numerical id from their username. (Ex: BurntSushi -> 189). -1 on failure."
    url = f'{BASE_URL}/users/{username}'
    response = requests.get(url)

    # If there was a problem getting a response return -1
    if response.status_code != requests.codes.ok:
        return -1

    user_data = json.loads(response.content)

    # If an error occurred then return with -1
    if user_data.contains('errors'):
        return -1

    # Try to grab their id and return -1 if something goes wrong
    # (which it shouldn't at this point but the API is badly documented so I added this for safety)
    return int(user_data.get('user', {}).get('id', -1))

def get_crate_result(crate: Dict[str, Union[str, int]]) -> Optional[CrateResult]:
    """Tries to convert a dictionary response from the api into a CrateResult. Returns None on error."""
    try:
        return CrateResult(crate['name'], crate['downloads'], crate['homepage'], crate['description'])
    except:
        return None

def get_crate_name_result(channel: Channel, name: str, params: dict) -> Optional[CrateResult]:
    """
    Get the result of searching for a specific crate by name
    :param channel: The channel to post any error messages in
    :param name: The name of the crate to search for
    :param params: The parameters to pass to the request
    :return: The api response as a dictionary or None on error
    """
    url = f'{BASE_URL}/crates/{name}'

    response = requests.get(url, params)

    # If there was a problem getting a response post a message to let the user know
    if response.status_code != requests.codes.ok:
        bot.post_message(channel, 'There was a problem getting a response.')
        return None

    raw_crate_result = json.loads(response.content)

    if raw_crate_result.contains('errors'):
        bot.post_message(channel, f"The requested crate {name} could not be found")
        return None

    # Convert the raw crate result to a CrateResult
    crate = get_crate_result(raw_crate_result)
    if crate is None:
        bot.post_message(channel, "There was a problem getting information about the crate")
        return None

    return crate

def get_crates_search_results(channel: Channel,
                              search: str,
                              params: dict,
                              page: int = 1,) -> Optional[Tuple[List[CrateResult], int]]:
    """
    Gets a list of crates and the total number of results from the api based on input parameters and the page number
    :param channel: The channel to post any error messages to
    :param search: The string to search for
    :param params: The parameters dictionary that gets passed to requests.get
    :param page: The page of the results to get from
    :return: (list of crates, total number of search results) or None if an error occurred
    """
    params['page'] = page
    params['letter'] = search

    url = BASE_URL + '/crates'
    response = requests.get(url, params)

    # If there was a problem getting a response post a message to let the user know
    if response.status_code != requests.codes.ok:
        bot.post_message(channel, 'There was a problem getting a response.')
        return None

    crates_results = json.loads(response.content)
    raw_crates = crates_results.get('crates', [])
    total = crates_results.get('meta', {}).get('total', 0)

    # Convert all of the crates to CrateResult
    crates = []
    for raw_crate in raw_crates:
        crate = get_crate_result(raw_crate)
        if crate is None:
            bot.post_message(channel, "There was a problem getting information about a crate")
            return None

        crates.append(crate)

    return crates, total

def handle_multiple_crate_search(channel: Channel, crates: List[dict]):
    pass
    # if not crates:
    #     bot.post_message(channel, "No crates were found")
    #     return None

    # # Iterate over all of the crates or until limit is reached. Whichever comes first.
    # for index in range(0, min(len(crates), args.limit) - 1):
    #     crate = crates[index]
    #     bot.post_message(channel, crate['name'])

def handle_single_crate_search(channel: Channel, name: str, params: dict):
    """
    Handles the case of searching for a single crate by name
    :param channel: The channel to post any results or errors to
    :param name: The name of the crate to search for
    :param params: Any additional parameters
    """
    crate = get_crate_name_result(channel, name, params)

    block = {
        'type': 'section',
        'text': {
            'type': 'mkdwn',
            'text': crate.name
        }
    }

def handle_crates_route(channel: Channel, args: CrateSearch):
    # Generate the parameters to search with
    params = {'sort': args.sort}

    if args.category:
        params['category'] = args.category

    # If the user parameter is already a number use it as an id otherwise try to get the id
    if args.user.isdigit():
        params['user_id'] = args.user
    elif args.user:
        user_id = get_user_id(args.user)
        if user_id == -1:
            bot.post_message(channel, f'The username {args.user} could not be resolved')
            return

        params['user_id'] = user_id

    # Change execution based on whether we are searching for a single specific crate or multiple crates
    if args.name:
        handle_single_crate_search(channel, params)
    else:
        handle_multiple_crate_search(channel, params)


def handle_categories_route(channel: Channel, args: CategorySearch):
    print("categories")
