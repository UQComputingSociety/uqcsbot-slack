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
        bot.post_message(command.channel_id, 'There was an error accessing the Urban Dictionary.')
        return
    results = http_response.json()

    # Sort definitions by their number of thumbs ups.
    sorted_defs = sorted(results['list'], key=lambda def_: def_['thumbs_up'], reverse=True)

    # If search phrase is not found, notify user.
    if len(sorted_defs) == 0:
        bot.post_message(command.channel_id, f'> No results found for {search_term}. ¯\\_(ツ)_/¯')
        return

    best_def = sorted_defs[0]
    # Break example into individual lines and wrap each in it's own block quote.
    example = best_def.get('example', '').split('\r\n')
    formatted_example = '\n'.join(f'> {line}' for line in example)

    # Format message and send response to user in channel query was sent from.
    message = f'*{search_term.title()}*\n' \
              f'{best_def["definition"].capitalize()}\n' \
              f'{formatted_example}'
    # Only link back to Urban Dictionary if there are more definitions.
    if len(sorted_defs) > 1:
        endpoint_url = http_response.url.replace(URBAN_API_ENDPOINT, URBAN_USER_ENDPOINT)
        message += f'\n_ more definitions at {endpoint_url} _'

    bot.post_message(command.channel_id, message)
