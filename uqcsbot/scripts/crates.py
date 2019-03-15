import argparse
import json
from enum import Enum
from typing import NamedTuple, Union, Optional, List, Dict, Tuple

import requests

from uqcsbot import bot, Command
from uqcsbot.api import Channel
from uqcsbot.utils.command_utils import loading_status, UsageSyntaxException

BASE_URL = "https://crates.io/api/v1"
MAX_LIMIT = 15  # The maximum number of search results from one call to the command

# NamedTuple for the case that the argparse finds a -h flag
HelpCommand = NamedTuple('HelpCommand', [('help_string', str)])

# NamedTuple for the default command that finds a crate by exact name match
ExactCrate = NamedTuple('ExactCrate', [('name', str)])

# NamedTuple for the search sub-command that deals with searching for specific crates
CrateSearch = NamedTuple('CrateSearch',
                         [('name', str), ('limit', int), ('category', str), ('user', str), ('sort', str),
                          ('search', str)])

# NamedTuple for the default categories sub-command that deals with searching for categories
CategorySearch = NamedTuple('CategorySearch', [('name', str), ('limit', int), ('sort', str)])

# NamedTuple for the user sub-command that deals with searching for specific users
UserSearch = NamedTuple('UserSearch', [('username', str)])

# Named tuple for a crate that was found in a search
CrateResult = NamedTuple('CrateResult', [('name', str), ('downloads', int), ('homepage', str), ('description', str)])


class SubCommand(Enum):
    """Distinguishes the type of sub command that was invoked"""
    EXACT = 1,
    SEARCH = 2,
    CATEGORIES = 3


@bot.on_command('crates')
@loading_status
def handle_crates(command: Command):
    """
    `!crates `
            - Get information about crates from crates.io
    """
    args = parse_arguments(command.arg if command.has_arg() else '')

    args.execute_action(command.channel_id, args)  # type: ignore


def parse_arguments(arg_str: str) -> Union[HelpCommand, CrateSearch, CategorySearch]:
    """
    Parses the arguments passed to the command
    :param arg_str: The argument string (not including "!crates")
    """
    parser = argparse.ArgumentParser(prog="!crates", add_help=False)
    subparsers = parser.add_subparsers()

    # Change the parsers default on error behaviour
    def usage_error(*args, **kwargs):
        raise UsageSyntaxException()

    # parser.error = usage_error  # type: ignore

    # Converts "Date and time" into "date-and-time" which is the format used for category ids
    def category_formatter(cat: str): return cat.lower().strip().replace(' ', '-')

    def search_limit(val: str): return max(1, min(int(val), MAX_LIMIT))  # limits the val such that 0 < val <= MaxLimit

    # For "!crates {args}"
    main_parser = subparsers.add_parser('main', add_help=False)
    main_parser.add_argument('name', nargs='?', default='', type=str.lower,
                             help="The name of the crate to get information about")
    main_parser.add_argument('-h', '--help', action='store_true', help='Prints this help message')
    main_parser.set_defaults(execute_action=handle_exact_crate_route, route=SubCommand.EXACT)

    # For !crates search {args}
    search_parser = subparsers.add_parser('search', add_help=False, help='Sub-command to search for a crate')
    search_parser.add_argument('search', nargs='?', default='', type=str.lower, help='The string to use for the search')
    search_parser.add_argument('-h', '--help', action='store_true', help='Prints this help message')
    search_parser.add_argument('-l', '--limit', default=5, type=search_limit,
                               help='When not searching for a specific crate how many results should be shown? '
                                    '(max: ' + str(MAX_LIMIT) + ', default: %(default)s)')
    search_parser.add_argument('-c', '--category', default='', type=category_formatter,
                               help="Limit results to crates in this category")
    search_parser.add_argument('-u', '--user', default='', type=str, help='Limit results by crate author')
    search_parser.add_argument('-o', '--sort', choices=['alpha', 'downloads'], default='downloads', type=str.lower,
                               help='Sort the results by alphabetical order or by number of downloads '
                                    '(default: %(default)s)')
    search_parser.set_defaults(execute_action=handle_search_crates_route, route=SubCommand.SEARCH)

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
    category_parser.set_defaults(execute_action=handle_categories_route, route=SubCommand.CATEGORIES)

    # TODO: For "!crates users {args}"

    # We need to check if the first argument is "categories" or "search" otherwise we add "main" to get around an
    # issue were argparse will complain that the name isn't one of the subparser names
    split_args = arg_str.split()
    if not split_args or (split_args[0] != "categories" and split_args[0] != "search"):
        split_args.insert(0, "main")

    args = parser.parse_args(split_args)

    # If the arguments show that help was requested then change the execute_action and add the correct help string
    if args.help:
        args.execute_action = handle_help_route
        if args.route == SubCommand.EXACT:
            # Because we had to break parser up into main this help message needs to be manually typed to be useful
            args.help_string = """
*Usage: !crates [[name] | {search,categories}]*

*Sub-Commands*:
 {search,categories}
   search              Search for a crate with conditions
   categories          Get information about categories instead of crates
   
*Default Usage*:
    usage: !crates [-h] [name]
    
    *Positional Arguments*:
     name        The exact name of the crate to get information about (use search for non-exact name)
    
    *Optional Arguments*:
     -h, --help  Prints this help message
            """
        elif args.route == SubCommand.SEARCH:
            args.help_string = search_parser.format_help()
        else:
            args.help_string = category_parser.format_help()

    return args


def handle_help_route(channel: Channel, args: HelpCommand):
    """This is called whenever the -h argument is invoked regardless of sub-command."""
    bot.post_message(channel, args.help_string)


def get_user_id(username: str) -> int:
    """"Tries to get the users numerical id from their username. (Ex: BurntSushi -> 189). -1 on failure."""
    url = f'{BASE_URL}/users/{username}'
    response = requests.get(url)

    # If there was a problem getting a response return -1
    if response.status_code != requests.codes.ok:
        return -1

    user_data = json.loads(response.content)

    # If an error occurred then return with -1
    if 'errors' in user_data:
        return -1

    # Try to grab their id and return -1 if something goes wrong
    # (which it shouldn't at this point but the API is badly documented so I added this for safety)
    return int(user_data.get('user', {}).get('id', -1))


def convert_crate_result(crate: Dict[str, Union[str, int]]) -> Optional[CrateResult]:
    """Tries to convert a dictionary response from the api into a CrateResult. Returns None on error."""
    try:
        # Sometimes the homepage is null so we try to grab something else if possible otherwise default to crates.io
        homepage = crate['homepage']
        homepage = crate['repository'] if homepage is None else homepage
        homepage = crate['documentation'] if homepage is None else homepage
        homepage = "https://crates.io" if homepage is None else homepage

        return CrateResult(crate['name'], crate['downloads'], homepage, crate['description'])
    except KeyError:
        return None


def get_crate_name_result(channel: Channel, name: str) -> Optional[CrateResult]:
    """
    Get the result of searching for a specific crate by name
    :param channel: The channel to post any error messages in
    :param name: The name of the crate to search for
    :return: The api response as a dictionary or None on error
    """
    url = f'{BASE_URL}/crates/{name}'

    response = requests.get(url)

    # If there was a problem getting a response post a message to let the user know
    if response.status_code != requests.codes.ok:
        bot.post_message(channel, 'There was a problem getting a response.')
        return None

    raw_crate_result = json.loads(response.content).get('crate', None)

    if raw_crate_result is None:
        bot.post_message(channel, "There was an issue getting the crate information")
        return None

    if 'errors' in raw_crate_result:
        bot.post_message(channel, f"The requested crate {name} could not be found")
        return None

    # Convert the raw crate result to a CrateResult
    crate = convert_crate_result(raw_crate_result)
    if crate is None:
        bot.post_message(channel, "There was a problem getting information about the crate")
        return None

    return crate


def get_crate_blocks(crate: CrateResult) -> List[Dict[str, Union[str, Dict[str, str], List[Dict[str, str]]]]]:
    """Converts a crate into its block based message format for posting to slack"""
    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*<{crate.homepage}|{crate.name}>*\n{crate.description}'
            },
        },
        {
            'type': 'context',
            'elements': [
                {
                    'type': 'plain_text',
                    'text': f'Downloads: {crate.downloads}'
                }
            ]
        },
        {
            'type': 'divider'
        }
    ]


def handle_exact_crate_route(channel: Channel, args: ExactCrate):
    """Handles what happens when a single crate is being searched for by exact name"""
    crate = get_crate_name_result(channel, args.name)
    if crate is None:
        return

    bot.post_message(channel, '', blocks=get_crate_blocks(crate))


def get_crates_search_results(channel: Channel,
                              search: str,
                              params: dict,
                              page: int = 1, ) -> Optional[Tuple[List[CrateResult], int]]:
    """
    Gets a list of crates and the total number of results from the api based on input parameters and the page number
    :param channel: The channel to post any error messages to
    :param search: The string to search for
    :param params: The parameters dictionary that gets passed to requests.get
    :param page: The page of the results to get from
    :return: (list of crates, total number of search results) or None if an error occurred
    """
    params['page'] = page

    if search:
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
        crate = convert_crate_result(raw_crate)
        if crate is None:
            bot.post_message(channel, "There was a problem getting information about a crate")
            return None

        crates.append(crate)

    return crates, total


def handle_search_crates_route(channel: Channel, args: CrateSearch):
    """Handles what happens when a crates are being searched for through multiple criteria"""
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

    search_result = get_crates_search_results(channel, args.search, params)
    if search_result is None:
        return

    crates, total = search_result

    # No crates at all were found
    if not crates:
        bot.post_message(channel, "No crates were found")
        return

    # The beginning of the formatted response
    blocks = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*Showing {min(args.limit, total)} of {total} results*'
            },
        },
        {
            'type': 'divider'
        }
    ]

    # Iterate over all of the crates or until limit is reached. Whichever comes first.
    page = 1
    remaining = args.limit
    while remaining > 0:
        amt = range(0, min(len(crates), remaining))
        for index in amt:
            crate = crates[index]
            blocks.extend(get_crate_blocks(crate))
            remaining -= 1

        page += 1
        search_result = get_crates_search_results(channel, args.search, params, page)
        if search_result is None or not search_result[0]:
            break

        crates, _ = search_result

    bot.post_message(channel, '', blocks=blocks)


def handle_categories_route(channel: Channel, args: CategorySearch):
    print("categories")


def handle_users_route(channel: Channel, args: UserSearch):
    print("users")
