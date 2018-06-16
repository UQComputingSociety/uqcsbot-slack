from uqcsbot import bot, Command
from uqcsbot.util.status_reacts import loading_status
import requests


URBAN_API_ENDPOINT = 'http://api.urbandictionary.com/v0/define'
URBAN_USER_ENDPOINT = 'https://www.urbandictionary.com/define.php'


@bot.on_command('urban')
@loading_status
def handle_urban(command: Command) -> None:
    """
    `!urban <PHRASE>` - Looks a phrase up on Urban Dictionary.
    """
    # Check for search phase
    if not command.has_arg():
        bot.post_message(command.channel, '> Usage: `!urban <SEARCH_PHRASE>`')
        return
    search_term = command.arg

    # Attempt to get definitions from the Urban Dictionary API.
    http_response = requests.get(URBAN_API_ENDPOINT, params={'term': search_term})
    if http_response.status_code != 200:
        bot.post_message(command.channel, 'There was an error accessing the Urban Dictionary API.')
        return
    results = http_response.json()

    # If search phrase is not found, notify user.
    if results['result_type'] != 'exact':
        bot.post_message(command.channel, f'> No results found for {search_term}. ¯\\_(ツ)_/¯')
        return

    # Get best definition (by most 'thumbs up') and construct response.
    sorted_definitions = sorted(results['list'], key=lambda definition: definition['thumbs_up'], reverse=True)
    best_definition = sorted_definitions[0]
    response_example = best_definition.get('example', '').replace('\r\n', '\n> ')  # Format example with block quotes.
    more_definitions = f'_ more definitions at {http_response.url.replace(URBAN_API_ENDPOINT, URBAN_USER_ENDPOINT)} _'

    # Format message and send response to user in channel query was sent from.
    message = f'*{search_term.title()}*\n{best_definition["definition"].capitalize()}\n> ' \
              f'{response_example}\n{more_definitions if len(sorted_definitions) > 1 else ""}'
    bot.post_message(command.channel, message)
