from uqcsbot import bot, Command
import requests
import json


@bot.on_command("wiki")
async def handle_wiki(command: Command):
    search = command.arg
    url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={search}&format=json"
    http_response = await bot.run_async(requests.get, url)
    response = json.loads(http_response.content)

    # If the results are empty let them know
    try:
        info = response[2][0]
    except IndexError:
        bot.post_message(command.channel, "No Results.\r\n")
        return

    # If it gives suggestions just return the first one
    typical = "may refer to:"
    if typical in info:
        bot.post_message(command.channel, response[2][1])
        return

    bot.post_message(command.channel, info)
