from uqcsbot import bot, Command
import requests
import json


@bot.on_command("wiki")
async def handle_wiki(command: Command):
    search_query = command.arg
    api_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&format=json"
    http_response = await bot.run_async(requests.get, api_url, params={'search': search_query})
    response = json.loads(http_response.content)

    result_list = 2
    url_list = 3
    best_match = 0
    first_suggestion = 1

    possible_matches = response[result_list]

    # If the results are empty let them know
    if not possible_matches:
        bot.post_message(command.channel, "No Results.")
        return

    info = possible_matches[best_match]
    url = response[url_list][best_match]

    # If it gives suggestions just return the first one
    suggestion_checks = ("may refer to:", "may have several meanings:")
    if any(check in info for check in suggestion_checks):
        # Don't have to set the url as the first suggestion is still the first index in the url_list
        info = possible_matches[first_suggestion]

    message = f'{info}\nLink: {url}'
    bot.post_message(command.channel, message)