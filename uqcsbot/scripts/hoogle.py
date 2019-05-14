from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
import requests
import json
import html
import re

def get_endpoint(type_sig: str) -> str:
    unescaped = html.unescape(type_sig)

    return "https://www.haskell.org/hoogle/?mode=json&hoogle=" + unescaped + "&start=0&count=10"


def pretty_hoogle_result(result: dict, is_verbose: bool) -> str:
    url = result['url']
    type_sig = re.sub('<[^<]+?>', '', result['item'])
    docs = re.sub('<[^<]+?>', '', result['docs']).replace('\n',' ').replace('&gt;&gt;&gt;','\n>')

    if is_verbose:
        return f"`{type_sig}` <{url}|link>\n{docs}"
    else:
        return f"`{type_sig}` <{url}|link>"


@bot.on_command("hoogle")
@loading_status
def handle_hoogle(command: Command):
    '''
    `!hoogle [-v] [--verbose] <TYPE_SIGNATURE>` - Queries the Hoogle Haskell API search engine,
    searching Haskell libraries by either function name, or by approximate type signature.
    '''
    command_args = command.arg.split() if command.has_arg() else []

    verbose = False

    if '--verbose' in command_args:
        command_args.remove('--verbose')
        verbose = True

    if '-v' in command_args:
        command_args.remove('-v')
        verbose = True

    if len(command_args) == 0:
        bot.post_message(command.channel_id, "usage: " + handle_hoogle.__doc__)
        return

    type_sig = ' '.join(command_args)

    endpoint_url = get_endpoint(type_sig)

    http_response = requests.get(endpoint_url)

    if http_response.status_code != requests.codes.ok:
        bot.post_message(command.channel_id, "Problem fetching data")
        return

    results = json.loads(http_response.content)

    if len(results) == 0:
        bot.post_message(command.channel_id, "No results found")
        return

    message = "\n".join(pretty_hoogle_result(result, verbose) for result in results)

    bot.post_message(command.channel_id, message)
