from uqcsbot import bot, Command
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from typing import List, Tuple
from functools import partial
import asyncio
from uqcsbot.utils.command_utils import UsageSyntaxException

BASE_URL = "http://acronyms.thefreedictionary.com"
LIST_COMMAND = ['ls', 'list', 'dir']
REGIONS = {
    'seq': {
        'aliases': ['brisbane', 'bne', 'brisvegas', 'qld', 'queensland'],
        'url': 'https://www.seqwater.com.au/dam-levels'
    }
}

@bot.on_command("water")
def handle_water(command: Command):
    """
    `!water <REGION>` - Prints the dam level for the region.

    `!water <LIST|LS|DIR>` - Prints a list of all regions.
    """
    if not command.has_arg():
        raise UsageSyntaxException()

    words = command.arg.split(' ')

    if len(words) > 1:
        raise UsageSyntaxException()

    response = []

    # Print the list of regions
    if words[0].lower() in LIST_COMMAND:
        response.append("Available regions:")
        for region in REGIONS:
            response.append(f">{region} (aliases: {', '.join(REGIONS[region]['aliases'])})")
    else:
        # Print the info for a specific region
        if words[0].lower() in REGIONS or words[0].lower() in [alias for region in REGIONS for alias in REGIONS[region]['aliases']]:
            actual_region = words[0].lower()
            name = words[0]
            if words[0].lower() not in REGIONS:    
                for region in REGIONS:
                    if words[0].lower() in REGIONS[region]['aliases']:
                        actual_region = region
                        name = region

            if actual_region == 'seq':
                http_response = requests.get(REGIONS[actual_region]['url'])
                html = BeautifulSoup(http_response.content, 'html.parser')

                maximum_prev_sibling = html.find("div", string='Full supply capacity')
                maximum_reading = maximum_prev_sibling.find_next_sibling("div")
                current_prev_sibling = html.find("div", string='Current capacity')
                current_reading = current_prev_sibling.find_next_sibling("div")

                maximum = int("".join(list(filter(str.isdigit, maximum_reading.get_text()))))
                current = int("".join(list(filter(str.isdigit, current_reading.get_text()))))
                percent = (1.0 * current / maximum) * 100.0

                response.append(f"{name} is at *{percent:3.2f}%* ({current:,}ML of {maximum:,}ML)")
            else:
                response.append(f"No region or alias found matching '{words[0]}'")    
        else:
            response.append(f"No region or alias found matching '{words[0]}'")

    bot.post_message(command.channel_id, '\r\n'.join(response))
