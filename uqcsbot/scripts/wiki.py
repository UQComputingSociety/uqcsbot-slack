from uqcsbot import bot, Command
import requests
import json


@bot.on_command("wiki")
async def handle_wiki(command: Command):
    search_query = command.arg
    url = f"https://en.wikipedia.org/w/api.php?action=opensearch&format=json"
    http_response = await bot.run_async(requests.get, url, params={'search': search_query})
    response = json.loads(http_response.content)

    result_list = 2
    best_match = 0
    first_suggestion = 1

    possible_matches = response[result_list]

    # If the results are empty let them know
    if not possible_matches[best_match]:
        bot.post_message(command.channel, "No Results.")
        return

    info = possible_matches[best_match]

    # If it gives suggestions just return the first one
    suggestion_checks = ("may refer to:", "may have several meanings:")
    if any(check in info for check in suggestion_checks):
        bot.post_message(command.channel, possible_matches[first_suggestion])
        return

    bot.post_message(command.channel, info)