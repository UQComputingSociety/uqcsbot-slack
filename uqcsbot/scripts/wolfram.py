from uqcsbot import bot, Command
from typing import Iterable, Tuple, Optional
from base64 import b64decode
import requests
import json

APP_ID = b64decode('RzU0S1VBLVVHWTdHR0hWUlg=').decode('utf-8')


def get_subpods(pods: list) -> Iterable[Tuple[str, dict]]:
    """
    Yields subpods in the order they should be displayed. A subpod is essentially an element of a wolfram response.
    For example one pod might be "Visual Representation" and the subpod is a graph of your input. Every pod has at least
    one subpod (usually only one).

    Yield: (pod_or_subpod_title, subpod)
    """
    for pod in pods:
        for subpod in pod["subpods"]:
            # Use the pods title if the subpod doesn't have its own title (general case)
            title = pod['title'] if len(subpod['title']) == 0 else subpod['title']
            yield (title, subpod)


# TODO: Better naming of commands
@bot.on_command("wolframfull")
async def handle_wolframfull(command: Command):
    """
    This posts the full results from wolfram query. Images and all

    Example usage:
    !wolframfull y = 2x + c
    """
    api_url = "http://api.wolframalpha.com/v2/query?&output=json"
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
        return

    # A pod is the name wolfram gives to the different "units" that make up its result.
    # For example a pod may be a "Visual Representation" of the input. Essentially they are logical components.
    # Each pod has one or more subpods that compose it.
    message = ""
    for title, subpod in get_subpods(result['pods']):
        plaintext = subpod["plaintext"]

        # Prefer a plain text representation to the image
        if plaintext != "" and plaintext != "* * * * * *":
            message += f'{title}: {plaintext}\n'
        else:
            image_url = subpod['img']['src']
            image_title = subpod['img']['title']
            message += f'{image_title}:\n{image_url}\n' if len(image_title) != 0 else f'{image_url}\n'

    bot.post_message(command.channel, message)


async def get_short_answer(search_query: str):
    """
    This uses wolfram's short answers api to just return a simple short plaintext response.

    This is used if the conversation api fails to get a result (for instance !wolfram pineapple is not a great
    conversation starter but may be interesting.
    """
    api_url = "http://api.wolframalpha.com/v2/result?"
    http_response = await bot.run_async(requests.get, api_url, params={'input': search_query, 'appid': APP_ID})

    # Check if the response is ok. A status code of 501 signifies that no result could be found.
    if http_response.status_code == 501:
        return "No short answer available. Try !wolframfull"
    elif http_response.status_code != requests.codes.ok:
        return "There was a problem getting the response"

    return http_response.content


@bot.on_command("wolfram")
async def handle_wolfram(command: Command):
    """
    This uses wolfram's conversation api to return a short response that can be replied to in a thread.
    If the response cannot be replied to a general short answer response is displayed instead.

    Example Usage:
    !wolfram Solve Newton's Second Law for mass
    !wolfram What is the distance from Earth to Mars?

    and then start a thread to continue the conversation
    """
    search_query = command.arg
    result, conversation_id, reply_host, s_output = await conversation_request(search_query)

    if conversation_id is None:
        if result == "No result is available":
            # If no conversational result is available just return a normal short answer
            short_response = await get_short_answer(search_query)
            bot.post_message(command.channel, short_response)
            return
        else:
            bot.post_message(command.channel, result)
            return

    # TODO: Is there a better option than storing the id in the fallback?
    # Here we store the conversation ID in the fallback so we can get it back later.
    # We also store an identifier string to check against later and the reply_host and s_output string
    # Attachments is a slack thing that allows the formatting or more complex messages. In this case we add a footer
    # and use the fallback to cheekily store information for later.
    attachments = [{
        'fallback': f'WolframCanReply {reply_host} {s_output} {conversation_id}',
        'footer': 'Further questions may be asked',
        'text': result,
    }]

    bot.post_message(command.channel, "", attachments=attachments)


def extract_reply(wolfram_response: dict) -> Tuple[str, str, str, str]:
    """
    Takes the response from the conversations API and returns it as a tuple containing the reply, conversation id,
    reply host and s parameters. In that order.
    """

    return (wolfram_response['result'],  # This is the answer to our question
            wolfram_response['conversationID'],  # Used to continue the conversation
            wolfram_response['host'],  # This is the hostname to ask the next question to
            wolfram_response.get('s', 'null'))  # s is only sometimes returned but is vital if it is returned


async def conversation_request(search_query: str, host_name: Optional[str]=None, conversation_id: Optional[str]=None, s_output: Optional[str]=None):
    """
    Makes a request for either the first stage of the conversation (don't supply a conversation_id and s_output or
    for a continued stage of the conversation (do supply them). It will return four values. In the case of an error
    it will return an error string that can be posted to the user and 3 Nones or it will return the result of the question,
    the new conversation_id, the new host name and the new s_output. In that order.
    """
    # The format of the api urls is slightly different if a conversation is being continued (has a conversation_id)
    # Any of the following would suffice but may as well be thorough
    if host_name is None or conversation_id is None or s_output is None:
        api_url = "http://api.wolframalpha.com/v1/conversation.jsp?"
        params = {'appid': APP_ID, 'i': search_query}
    else:
        # Slack annoyingly formats the reply_host link so we have to extract what we want:
        # The format is <http://www.domain.com|www.domain.com>
        host_name = host_name[1:-1].split('|')[0]
        api_url = f'{host_name}/api/v1/conversation.jsp?'
        params = {'appid': APP_ID, 'i': search_query, 'conversationid': conversation_id, 's': s_output}


    http_response = await bot.run_async(requests.get, api_url, params=params)

    if http_response.status_code != requests.codes.ok:
        return "There was a problem getting the response", None, None, None

    # Convert to json and check for an error
    wolfram_answer = json.loads(http_response.content)
    if 'error' in wolfram_answer:
        return wolfram_answer['error'], None, None, None

    return extract_reply(wolfram_answer)


@bot.on('message')
async def handle_reply(evt: dict):
    """
    Handles a message event. Whenever a message is a reply to one of !wolframs conversational results this handles
    getting the next response and updating the old stored information.
    """
    # If the message isn't from a thread or is from a bot ignore it (avoid those infinite loops)
    if 'thread_ts' not in evt or evt.get('subtype') == 'bot_message':
        return

    channel = evt['channel']
    thread_ts = evt['thread_ts']  # This refers to time the original message
    thread_parent = bot.api.conversations.history(channel=channel, limit=1, inclusive=True, latest=thread_ts)

    if not thread_parent['ok']:
        # The most likely reason for this error is auth issues or possibly rate limiting
        bot.post_message(channel, 'Sorry, something went wrong with slack', thread_ts=thread_ts)
        return

    # Limit=1 was used so the first (and only) message is what we want
    parent_message = thread_parent['messages'][0]
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
    s_output = '' if s_output == 'null' else s_output

    # Ask Wolfram for the new answer grab the new stuff and post the reply.
    reply, conversation_id, reply_host, s_output = await conversation_request(new_question, reply_host, conversation_id, s_output)

    bot.post_message(channel, reply, thread_ts=thread_ts)

    # If getting a the conversation request results in an error then conversation_id will be None
    if conversation_id is not None:
        # Update the old fallback to reflect the new state of the conversation
        parent_attachments['fallback'] = f'WolframCanReply {reply_host} {s_output} {conversation_id}'

        bot.api.chat.update(channel=channel, attachments=[parent_attachments], ts=thread_ts)