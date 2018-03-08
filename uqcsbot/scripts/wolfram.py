from uqcsbot import bot, Command
from typing import Iterable, Tuple
import requests
import json

APP_ID = "UVKV2V-5XW2TETT69"


# IDEA: Show the assumptions made?
# TODO: Better naming of commands
@bot.on_command("wolframfull")
async def handle_wolframfull(command: Command):
    """
    This posts the full results from wolfram query. Images and all

    Example usage:
    !wolframfull y = 2x + c
    """
    api_url = r"http://api.wolframalpha.com/v2/query?&output=json"
    search_query = command.arg
    http_response = await bot.run_async(requests.get, api_url, params={'input': search_query, 'appid': APP_ID})

    # Check if the response is ok
    if http_response.status_code != requests.codes.ok:
        bot.post_message(command.channel, "There was a problem getting the response")
        return

    # Get the result of the query and determine if wolfram succeeded in evaluating it
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
            await short_answer(command)
            return
        else:
            bot.post_message(command.channel, error)
            return

    result = json_response['result']
    reply_host = json_response['host']
    conversation_id = json_response['conversationID']
    s_output = json_response.get('s', None)

    # TODO: Is there a better option than storing the id in the fallback?
    # Here we store the conversation ID in the fallback so we can get it back later. We also store and indicator of this
    attachments = [{
        'fallback': f'WolframCanReply {reply_host} {s_output} {conversation_id}',
        'footer': 'Further questions may be asked',
        'text': result,
    }]

    bot.post_message(command.channel, "", attachments=attachments)

# TODO: Add 'ok' checks
@bot.on('message')
async def handle_reply(evt: dict):
    # If the message isn't from a thread or is from a bot ignore it (avoid those infinite loops)
    if 'thread_ts' not in evt or ('subtype' in evt and evt['subtype'] == 'bot_message'):
        return

    channel = evt['channel']

    thread_ts = evt['thread_ts']
    thread_parent = bot.api.conversations.history(channel=channel, limit=1, inclusive=True, latest=thread_ts)

    if not thread_parent['ok']:
        bot.post_message(channel, 'Sorry, something went wrong with slack', thread_ts=thread_ts)
        return

    parent_message = thread_parent['messages'][0]
    # If the threads parent wasn't by a bot ignore
    if 'subtype' not in parent_message or parent_message['subtype'] != 'bot_message':
        return

    # Finally, we have to check that this is a Wolfram replyable message
    # It is rare we would reach this point and not pass as who replies to a bot in a thread for another reason
    parent_attachments = parent_message['attachments'][0]
    parent_fallback = parent_attachments['fallback']
    if 'WolframCanReply' not in parent_fallback:
        return

    # Now we can grab the conversation_id from the message and get the new question (s only sometimes appears)
    _, reply_host, s_output, conversation_id = parent_fallback.split(' ')
    new_question = evt['text']
    s_output = '' if s_output == 'None' else s_output

    # Slack annoyingly formats the reply_host link so we have to extract what we want:
    reply_host = reply_host[1:-1].split('|')[0]

    # Now we can ask Wolfram for the next answer:
    api_url = f'{reply_host}/api/v1/conversation.jsp?'
    params = {'appid': APP_ID, 'i': new_question, 'conversationid': conversation_id, 's': s_output}
    http_response = await bot.run_async(requests.get, api_url, params=params)

    if http_response.status_code != requests.codes.ok:
        bot.post_message(channel, "There was a problem getting the response", thread_ts=thread_ts)
        return

    # Convert to json and check for an error
    json_response = json.loads(http_response.content)
    if 'error' in json_response:
        bot.post_message(channel, json_response['error'], thread_ts=thread_ts)
        return

    # Otherwise grab the new stuff and post the reply.
    reply = json_response['result']
    conversation_id = json_response['conversationID']
    reply_host = json_response['host']
    s_output = json_response.get('s', None)

    bot.post_message(channel, reply, thread_ts=thread_ts)

    # Update the old conversation_id to indicate the new state
    updated_attachments = parent_attachments.copy()
    updated_attachments['fallback'] = f'WolframCanReply {reply_host} {s_output} {conversation_id}'

    bot.api.chat.update(channel=channel, attachments=[updated_attachments], ts=thread_ts)


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
