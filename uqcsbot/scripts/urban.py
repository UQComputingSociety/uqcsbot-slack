import re
import requests
from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status, UsageSyntaxException

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
        raise UsageSyntaxException()

    search_term = command.arg

    # Attempt to get definitions from the Urban Dictionary API.
    http_response = requests.get(URBAN_API_ENDPOINT, params={'term': search_term})
    if http_response.status_code != 200:
        bot.post_message(command.channel_id, 'There was an error accessing the Urban Dictionary API.')
        return
    results = http_response.json()

    # Filter for exact matches
    filtered_definitions = filter(lambda def_: def_['word'].casefold() == search_term.casefold(), results['list'])

    # Sort definitions by their number of thumbs ups.
    sorted_definitions = sorted(filtered_definitions, key=lambda def_: def_['thumbs_up'], reverse=True)

    # If search phrase is not found, notify user.
    if len(sorted_definitions) == 0:
        bot.post_message(command.channel_id, f'> No results found for {search_term}. ¯\\_(ツ)_/¯')
        return

    best_definition = sorted_definitions[0]
    best_definition_text = re.sub(r'[\[\]]', '', best_definition["definition"])  # Remove Urban Dictionary [links]

    example_text = re.sub(r'[\[\]]', '', best_definition.get('example', '')) # Remove Urban Dictionary [links]
    # Break example into individual lines and wrap each in it's own block quote.
    example_lines = example_text.split('\r\n')
    formatted_example = '\n'.join(f'> {line}' for line in example_lines)

    # Format message and send response to user in channel query was sent from.
    message = f'*{search_term.title()}*\n' \
              f'{best_definition_text.capitalize()}\n' \
              f'{formatted_example}'
    # Only link back to Urban Dictionary if there are more definitions.
    if len(sorted_definitions) > 1:
        endpoint_url = http_response.url.replace(URBAN_API_ENDPOINT, URBAN_USER_ENDPOINT)
        message += f'\n_ more definitions at {endpoint_url} _'

    bot.post_message(command.channel_id, message)
