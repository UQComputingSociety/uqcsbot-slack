from uqcsbot import bot, Command
from typing import Iterable, Tuple
import requests
import json

APP_ID = "UVKV2V-5XW2TETT69"


# TODO: Show the assumptions made?
# TODO: Better naming of commands
@bot.on_command("wolframfull")
async def handle_wolframfull(command: Command):
    """This posts the full results from wolfram query. Images and all"""
    api_url = r"http://api.wolframalpha.com/v2/query?&output=json"
    search_query = command.arg
    http_response = await bot.run_async(requests.get, api_url, params={'input': search_query, 'appid': APP_ID})

    # Check if the response is ok
    if http_response.status_code != requests.codes.ok:
        bot.post_message(command.channel, "There was a problem getting the response")
        return

    # Get the result of the query and determine if wolfram succeeded in evaluating it
    # TODO: success and error mean slightly different things. The message could indicate this?
    result = json.loads(http_response.content)['queryresult']
    if not result['success'] or result["error"]:
        bot.post_message(command.channel, "Please rephrase your query. Wolfram could not compute.")

    subpods = get_subpods(result['pods'])

    message = ""
    for title, subpod in subpods:
        plaintext = subpod["plaintext"]

        # Prefer a plain text representation to the image
        if plaintext != "" and plaintext != "* * * * * *":
            message += f'{title}: {plaintext}\n'
        else:
            image_url = subpod['img']['src']
            image_title = subpod['img']['title']
            message += f'{image_title}:\n{image_url}\n' if image_title else f'{image_url}\n'

    bot.post_message(command.channel, message)


@bot.on_command("wolfram")
async def handle_wolfram(command: Command):
    """This uses wolfram's conversation api to return a short response that can be replied to in a thread"""
    api_url = r"http://api.wolframalpha.com/v1/conversation.jsp"
    search_query = command.arg
    http_response = await bot.run_async(requests.get, api_url, params={'input': search_query, 'appid': APP_ID})

    # Check if the response is okay
    if http_response.status_code != requests.codes.ok:
        bot.post_message(command.channel, "There was a problem getting the response")
        return

    json_response = json.loads(http_response.content)

    if 'error' in json_response:
        error = json_response['error']
        if error == "No result is available":
            # If no conversational result is available just return a normal short answer
            # TODO: Should the user be told they can't reply to the result?
            await short_answer(command)
            return
        else:
            bot.post_message(command.channel, error)
            return

    result = json_response['result']
    conversation_id = json_response['conversationID']

    attachments = [{'footer': str(conversation_id)}]
    bot.post_message(command.channel, result, attachments=attachments)

@bot.on('message')
def handle_reply(evt: dict):
    # We only care about replies to messages that have been set up for conversation
    if 'subtype' not in evt or evt['subtype'] != 'message_replied':
        return

    bot.post_message(evt['channel'], evt)

async def short_answer(command: Command):
    """
    This uses wolfram's short answers api to just return a simple short plaintext response.

    This is used if the conversation api fails to get a result (for instance !wolfram pineapple is not a great
    conversation starter but may be interesting.
    """
    api_url = r"http://api.wolframalpha.com/v1/result?"
    search_query = command.arg
    http_response = await bot.run_async(requests.get, api_url, params={'input': search_query, 'appid': APP_ID})

    # Check if the response is ok. A status code of 501 signifies that no result could be found.
    if http_response.status_code == 501:
        bot.post_message(command.channel, "No short answer available. Try !wolframfull")
        return
    elif http_response.status_code != requests.codes.ok:
        bot.post_message(command.channel, "There was a problem getting the response")
        return

    bot.post_message(command.channel, http_response.content)

def get_subpods(pods: list) -> Iterable[Tuple[str, dict]]:
    """Yields sublots in the order they should be displayed"""
    for pod in pods:
        for subpod in pod["subpods"]:
            # Use the pods title if the subpod doesn't have its own title (general case)
            title = subpod['title'] if subpod['title'] else pod['title']
            yield (title, subpod)
