from uqcsbot import bot, Command
import requests
import json


@bot.on_command("wiki")
async def handle_wiki(command: Command):
    search_query = command.arg
    api_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&format=json"
    http_response = await bot.run_async(requests.get, api_url, params={'search': search_query})
    _, title_list, snippet_list, url_list = json.loads(http_response.content)

    first_snippet = 0
    suggestion_snippet = 1

    # If the results are empty let them know. Any list being empty signifies this.
    if len(title_list) == 0:
        bot.post_message(command.channel, "No Results Found.")
        return

    info = snippet_list[first_snippet]

    # If info is a suggestion signifier (see suggestion_checks) then use the second snippet (has content)
    suggestion_checks = ("may refer to:", "may have several meanings:")
    if any(check in info for check in suggestion_checks):
        info = title_list[suggestion_snippet]

    # The first url and title matches the first snippet containing any content
    message = f'{title_list[0]}: {info}\nLink: {url}'
    bot.post_message(command.channel, message)