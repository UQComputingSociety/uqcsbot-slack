from uqcsbot import bot, Command
import requests
import json

API_URL = "http://api.pearson.com/v2/dictionaries/laad3/entries?limit=1"

@bot.on_command("define")
def define(command: Command):
    '''
    `!define <TEXT>` - Gets the dictionary definition of TEXT
    '''
    query = command.arg
    # Fun Fact: Empty searches return the definition of adagio (a piece of music to be played or sung slowly)
    if not command.has_arg():
        bot.post_message(command.channel, "Please specify a word")
        return

    http_response = requests.get(API_URL, params={'headword': query})

    # Check if the response is OK
    if http_response.status_code != requests.codes.ok:
        bot.post_message(command.channel, "Problem fetching definition")
        return

    json_data = json.loads(http_response.content)
    results = json_data.get('results', [])
    if len(results) == 0:
        message = "No Results"
    else:
        # This gets the first definition of the first result.
        senses = results[0].get('senses', [{}])[0]
        # Sometimes there are "subsenses" for whatever reason and sometimes there aren't. No explanation provided.
        # This gets the first subsense if there are otherwise just uses senses.
        message = senses.get('subsenses', [senses])[0].get('definition', "Definition not available")

    bot.post_message(command.channel, f">>>{message}")
