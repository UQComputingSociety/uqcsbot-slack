from uqcsbot import bot, Command
import requests
import json

API_URL = r"http://api.wolframalpha.com/v2/query?appid=UVKV2V-5XW2TETT69&output=json"


@bot.on_command("wolfram")
async def handle_wolfram(command: Command):
    search_query = command.arg
    http_response = await bot.run_async(requests.get, API_URL, params={'input': search_query})

    # Check if the response is ok
    if http_response.status_code != requests.codes.ok:
        bot.post_message(command.channel, "There was a problem getting the response")
        return

    # Get the result of the query and determine if wolfram succeeded in evaluating it
    # TODO: success and error mean slightly different things. The message could indicate this?
    result = json.loads(http_response.content)['queryresult']
    if not result['success'] or result["error"]:
        bot.post_message(command.channel, "Please rephrase your query. Wolfram could not compute.")



