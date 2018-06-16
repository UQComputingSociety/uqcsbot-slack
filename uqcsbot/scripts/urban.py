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
        bot.post_message(command.channel_id, '> Usage: `!urban <SEARCH_PHRASE>`')
        return
    search_term = command.arg

    # Attempt to get definitions from the Urban Dictionary API.
    http_response = requests.get(URBAN_API_ENDPOINT, params={'term': search_term})
    if http_response.status_code != 200:
        bot.post_message(command.channel_id, 'There was an error accessing the Urban Dictionary API.')
        return
    results = http_response.json()

    # If search phrase is not found, notify user.
    if results['result_type'] != 'exact':
        bot.post_message(command.channel_id, f'> No results found for {search_term}. ¯\\_(ツ)_/¯')
        return

    # Get best definition (by most 'thumbs up') and construct response.
    sorted_defs = sorted(results['list'], key=lambda definition: definition['thumbs_up'], reverse=True)
    best_def = sorted_defs[0]
    example = best_def.get('example', '').split('\r\n')  # Break example into individual lines.
    formatted_example = '\n'.join(f'> {line}' for line in example)  # Put each line of the example in a block quote.

    # Format message and send response to user in channel query was sent from.
    message = f'*{search_term.title()}*\n' \
              f'{best_def["definition"].capitalize()}\n' \
              f'{formatted_example}'
    # Only link back to Urban Dictionary if there are more definitions.
    if len(sorted_defs) > 1:
        endpoint_url = http_response.url.replace(URBAN_API_ENDPOINT, URBAN_USER_ENDPOINT)
        message += f'\n_ more definitions at {endpoint_url} _'

    bot.post_message(command.channel_id, message)
