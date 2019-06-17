import os
import sys
import importlib
import logging
import argparse
from base64 import b64decode
import json
import requests
from uqcsbot.base import bot, Command, UQCSBot  # noqa

LOGGER = logging.getLogger("uqcsbot")

SLACK_VERIFICATION_TOKEN = os.environ.get("SLACK_VERIFICATION_TOKEN", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
# Channel group which contains all the bots. Easy way to get all their ids.
SECRET_BOT_MEETING_ROOM = 'G9JJXHF7S'

# UQCSTesting tokens. Everything is base64 encoded to
# somewhat circumvent token tracking by GitHub etal.
#
# Order: uqcsbot-alpha, uqcsbot-beta, uqcsbot-gamma, uqcsbot-delta
BOT_TOKENS = {'U9LA6BX8X': 'eG94Yi0zMjYzNDY0MDUzMDMteGpIbFhlamVNUG1McVhRSnNnZFoyZVhT',
              'U9K81NL7N': 'eG94Yi0zMjUyNzM3NjgyNjAtNFd0SGhRUWhLb3BSVUlJNFJuc0VRRXJL',
              'U9JJZ1ZJ4': 'eG94Yi0zMjQ2NDUwNjc2MTYtaHNpR3B3S0ZhSnY3bzJrOW43UU9uRXFp',
              'U9K5W508K': 'eG94Yi0zMjUyMDAxNzAyOTEtTlJvdVVLcWdyVEpVSE9SMjBoUzhBcnhW'}
for key in BOT_TOKENS:
    BOT_TOKENS[key] = b64decode(BOT_TOKENS[key]).decode('utf-8')

# Mitch's UQCSTesting Slack API Token. No touchie >:(
UQCSTESTING_USER_TOKEN = b64decode('eG94cC0yNjA3ODI2NzQ2MTAtMjYwMzQ1MTQ0NTI5LTMyNTEyMzU5ODExNS01Yj'
                                   'dmYjlhYzAyZWYzNDAyNTYyMTJmY2Q2YjQ1NmEyYg==').decode('utf-8')


def get_user_info(user_id):
    """
    Returns info about a user

    See https://api.slack.com/methods/users.info for the contents of info
    """
    api_url = 'https://slack.com/api/users.info'
    response = requests.get(api_url, params={'token': UQCSTESTING_USER_TOKEN, 'user': user_id})

    if response.status_code != requests.codes['ok']:
        LOGGER.error(f'Received status code {response.status.code}')
        sys.exit(1)

    json_contents = json.loads(response.content)
    if not json_contents['ok']:
        LOGGER.error(json_contents['error'])
        sys.exit(1)

    return json_contents


def is_active_bot(user_info):
    """
    Returns true if the provided user info describes an active bot (i.e. not deleted)
    """
    if not user_info['ok']:
        return False
    user = user_info['user']
    return user.get('is_bot', False) and not user['deleted']


def is_bot_avaliable(user_id):
    """
    Returns true if the given user_id is an active bot that is available (i.e. is
    not currently 'active' which would mean it is in use by another user).
    """

    api_url = 'https://slack.com/api/users.getPresence'
    response = requests.get(api_url, params={'token': UQCSTESTING_USER_TOKEN, 'user': user_id})
    if response.status_code != requests.codes['ok']:
        return False

    json_contents = json.loads(response.content)
    return json_contents['ok'] and json_contents['presence'] == 'away'


def get_free_test_bot():
    """
    Pings a channel on the UQCSTesting Slack that contains all the available
    bots, and Mitch. We can poll this channel to find  bots which are 'away'
    (that is, not currently being used by anyone else)

    Returns info about the bot

    See https://api.slack.com/methods/users.info for the contents of info
    """
    api_url = 'https://slack.com/api/conversations.members'
    response = requests.get(api_url, params={'token': UQCSTESTING_USER_TOKEN,
                                             'channel': SECRET_BOT_MEETING_ROOM})
    if response.status_code != requests.codes['ok']:
        LOGGER.error(f'Received status code {response.status.code}')
        sys.exit(1)

    json_contents = json.loads(response.content)
    if not json_contents['ok']:
        LOGGER.error(json_contents['error'])
        sys.exit(1)

    for user_id in json_contents['members']:
        info = get_user_info(user_id)
        if is_active_bot(info) and is_bot_avaliable(user_id):
            return info
    return None


def import_scripts():
    dir_path = os.path.dirname(__file__)
    scripts_dir = os.path.join(dir_path, 'scripts')
    for sub_file in os.listdir(scripts_dir):
        if not sub_file.endswith('.py') or sub_file == '__init__.py':
            continue
        module = f'uqcsbot.scripts.{sub_file[:-3]}'
        importlib.import_module(module)


def main():
    # Import scripts
    import_scripts()

    # Setup the CLI argument parser
    parser = argparse.ArgumentParser(description='Run UQCSBot')
    parser.add_argument('--dev', dest='dev',
                        action='store_true',
                        help='Runs the bot in development mode (auto assigns a '
                             'bot on the uqcstesting Slack team)')
    parser.add_argument('--log_level', dest='log_level',
                        default='INFO',
                        help='Specifies the output logging level to be used '
                             '(i.e. DEBUG, INFO, WARNING, ERROR, CRITICAL)')

    # Retrieve the CLI args
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)

    # If in development mode, attempt to allocate an available bot token,
    # else stick with the default. If no bot could be allocated, exit.
    bot_token = SLACK_BOT_TOKEN
    if args.dev:
        test_bot = get_free_test_bot()
        if test_bot is None:
            LOGGER.error('Something went wrong during bot allocation. Please ensure there'
                         ' are bots available and try again later. Exiting.')
            sys.exit(1)
        bot_token = BOT_TOKENS.get(test_bot['user']['id'], None)
        LOGGER.info("Bot name: " + test_bot['user']['name'])

    if bot_token is None or bot_token == "":
        LOGGER.error("No bot token found!")
        sys.exit(1)

    bot.run(bot_token, SLACK_VERIFICATION_TOKEN)


if __name__ == "__main__":
    main()
