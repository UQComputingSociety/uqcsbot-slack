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
    """
    This uses wolfram's conversation api to return a short response that can be replied to in a thread.
    If the response cannot be replied to a general short answer response is displayed instead.

    Example Usage:
    !wolfram Solve Newton's Second Law for mass
    !wolfram What is the distance from Earth to Mars?

    and then start a thread to continue to conversation
    """
    api_url = r"http://api.wolframalpha.com/v1/conversation.jsp"
    search_query = command.arg
    http_response = await bot.run_async(requests.get, api_url, params={'input': search_query, 'appid': APP_ID})

    # Check if the response is okay
    if http_response.status_code != requests.codes.ok:
        bot.post_message(command.channel, "There was a problem getting the response")
        return

    wolfram_result = json.loads(http_response.content)
    if 'error' in wolfram_result:
        error = wolfram_result['error']
        if error == "No result is available":
            # If no conversational result is available just return a normal short answer
            short_response = await short_answer(search_query)
            bot.post_message(command.channel, short_response)
            return
        else:
            bot.post_message(command.channel, error)
            return

    # Unpack the response in order to construct the reply message
    result = wolfram_result['result']  # This is the answer to our question
    reply_host = wolfram_result['host']  # This is the hostname to ask the next question to
    conversation_id = wolfram_result['conversationID']  # Used to continue the conversation
    s_output = wolfram_result.get('s', None)  # s is only sometimes returned but is vital if it is returned

    # TODO: Is there a better option than storing the id in the fallback?
    # Here we store the conversation ID in the fallback so we can get it back later.
    # We also store an identifier string to check against later and the reply_host and s_output string
    attachments = [{
        'fallback': f'WolframCanReply {reply_host} {s_output} {conversation_id}',
        'footer': 'Further questions may be asked',
        'text': result,
    }]

    bot.post_message(command.channel, "", attachments=attachments)


@bot.on('message')
async def handle_reply(evt: dict):
    # If the message isn't from a thread or is from a bot ignore it (avoid those infinite loops)
    if 'thread_ts' not in evt or (evt.get('subtype') == 'bot_message'):
        return

    channel = evt['channel']
    thread_ts = evt['thread_ts']  # This refers to time the original message
    thread_parent = bot.api.conversations.history(channel=channel, limit=1, inclusive=True, latest=thread_ts)

    if not thread_parent['ok']:
        bot.post_message(channel, 'Sorry, something went wrong with slack', thread_ts=thread_ts)
        return

    parent_message = thread_parent['messages'][0]  # Limit=1 was used so the first (and only) message is what we want
    # If the threads parent wasn't by a bot ignore it
    if parent_message.get('subtype') != 'bot_message':
        return

    # Finally, we have to check that this is a Wolfram replyable message
    # It is rare we would reach this point and not pass as who replies to a bot in a thread for another reason?
    parent_attachments = parent_message['attachments'][0]  # The message is formatted with only one attachment
    parent_fallback = parent_attachments['fallback']
    if 'WolframCanReply' not in parent_fallback:
        return

    # Now we can grab the conversation_id from the message and get the new question (s only sometimes appears)
    # Recall the format of the fallback "identifier hostname s_output conversationID"
    _, reply_host, s_output, conversation_id = parent_fallback.split(' ')
    new_question = evt['text']  # This is the value of the message that triggered this whole response
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
    wolfram_answer = json.loads(http_response.content)
    if 'error' in wolfram_answer:
        bot.post_message(channel, wolfram_answer['error'], thread_ts=thread_ts)
        return

    # Otherwise grab the new stuff and post the reply.
    reply = wolfram_answer['result']
    conversation_id = wolfram_answer['conversationID']
    reply_host = wolfram_answer['host']
    s_output = wolfram_answer.get('s', None)

    bot.post_message(channel, reply, thread_ts=thread_ts)

    # Update the old fallback to reflect the new state of the conversation
    parent_attachments['fallback'] = f'WolframCanReply {reply_host} {s_output} {conversation_id}'

    bot.api.chat.update(channel=channel, attachments=[parent_attachments], ts=thread_ts)


async def short_answer(search_query: str):
    """
    This uses wolfram's short answers api to just return a simple short plaintext response.

    This is used if the conversation api fails to get a result (for instance !wolfram pineapple is not a great
    conversation starter but may be interesting.
    """
    api_url = r"http://api.wolframalpha.com/v1/result?"
    http_response = await bot.run_async(requests.get, api_url, params={'input': search_query, 'appid': APP_ID})

    # Check if the response is ok. A status code of 501 signifies that no result could be found.
    if http_response.status_code == 501:
        return "No short answer available. Try !wolframfull"
    elif http_response.status_code != requests.codes.ok:
        return "There was a problem getting the response"

    return http_response.content


def get_subpods(pods: list) -> Iterable[Tuple[str, dict]]:
    """
    Yields subpods in the order they should be displayed

    Yield: (pod_or_subpod_title, subpod)
    """
    for pod in pods:
        for subpod in pod["subpods"]:
            # Use the pods title if the subpod doesn't have its own title (general case)
            title = subpod['title'] if subpod['title'] else pod['title']
            yield (title, subpod)
