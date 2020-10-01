from requests import get
from xml.etree.ElementTree import fromstring
from difflib import SequenceMatcher
from html import unescape

from typing import Dict, Optional, Any

from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import UsageSyntaxException, loading_status


def get_bgg_id(search_name: str) -> Optional[str]:
    """
    returns the bgg id, searching by name
    """
    query = get(f"https://www.boardgamegeek.com/xmlapi2/"
                + f"search?type=boardgame,boardgameexpansion&query={search_name:s}")
    if query.status_code != 200:
        return None
    results = fromstring(query.text)
    if results.get("total", "0") == "0":
        return None

    # filters for the closest name match
    match = {}
    for i in results:
        if i.get("id") is None:
            continue
        for j in i:
            if j.tag == "name":
                match[i.get("id")] = SequenceMatcher(None, search_name, j.get("value")).ratio()
    return max(match, key=match.get)


def get_board_game_parameters(identity: str) -> Optional[dict]:
    """
    returns the various parameters of a board game from bgg
    """
    query = get(f"https://www.boardgamegeek.com/xmlapi2/thing?stats=1&id={identity:s}")
    if query.status_code != 200:
        return None
    result = fromstring(query.text)[0]
    parameters: Dict[str, Any] = {}
    parameters["categories"] = set()
    parameters["mechanics"] = set()
    parameters["subranks"] = {}
    parameters["identity"] = identity

    for i in result:
        # sets the range of players
        if i.tag == "poll" and i.attrib.get("name") == "suggested_numplayers":
            players = set()
            for j in i:
                votes = 0
                for k in j:
                    votes += (int(k.attrib["numvotes"])
                              * (-1 if k.attrib["value"] == "Not Recommended" else 1))
                if votes > 0:
                    players.add(j.attrib["numplayers"])
            if players:
                parameters["min_players"] = min(players)
                parameters["max_players"] = max(players)
        # sets the name of the board game
        elif i.tag == "name" and i.attrib.get("type") == "primary":
            parameters["name"] = i.attrib["value"]
        # adds a category
        elif i.tag == "link" and i.attrib.get("type") == "boardgamecategory":
            parameters["categories"].add(i.attrib["value"])
        # adds a mechanic
        elif i.tag == "link" and i.attrib.get("type") == "boardgamemechanic":
            parameters["mechanics"].add(i.attrib["value"])
        # sets the user ratings
        elif i.tag == "statistics":
            for j in i[0]:
                if j.tag == "average":
                    parameters["score"] = j.attrib["value"]
                if j.tag == "usersrated":
                    parameters["users"] = j.attrib["value"]
                if j.tag == "ranks":
                    for k in j:
                        if (k.attrib.get("name") == "boardgame"
                            and k.attrib.get("value").isnumeric()):
                            n = int(k.attrib.get("value"))
                            o = "tsnrhtdd"[(n/10 % 10 != 1) * (n % 10 < 4) * n % 10::4]
                            parameters["rank"] = f"{n:d}{o:s}"
                        elif k.attrib.get("value").isnumeric():
                            n = int(k.attrib.get("value"))
                            o = "tsnrhtdd"[(n/10 % 10 != 1) * (n % 10 < 4) * n % 10::4]
                            s = " ".join(k.attrib["friendlyname"].split(" ")[:-1])
                            parameters["subranks"][s] = f"{n:d}{o:s}"
        # sets the discription
        elif i.tag == "description":
            parameters["description"] = i.text
        # sets the minimum playing time
        elif i.tag == "minplaytime":
            parameters["min_time"] = i.attrib["value"]
        elif i.tag == "maxplaytime":
            parameters["max_time"] = i.attrib["value"]

    return parameters


def format_board_game_parameters(parameters: dict) -> str:
    message = (f"*{parameters.get('name', ':question:'):s}*\n"
               f"A board game for {parameters.get('min_players', ':question:'):s} to"
               + f" {parameters.get('max_players', ':question:'):s} players, with a"
               + f" playing time of {parameters.get('min_time', ':question:'):s} minutes"
               + ("" if parameters.get('min_time') == parameters.get('max_time')
                  else f" to {parameters.get('max_time', ':question:'):s} minutes") + ".\n"
               f"Rated {parameters.get('score', ':question:'):s}/10 by"
               + f" {parameters.get('users', ':question:'):s} users.\n"
               f"Ranked {parameters.get('rank', ':question:'):s} overall on _Board Game Geek_.\n"
               + "".join(f"• Ranked {value:s} in the {key:s} category.\n"
                         for key, value in parameters.get("subranks", {}).items()) +
               f"Categories: {', '.join(parameters.get('categories', set())):s}\n"
               f"Mechanics: {', '.join(parameters.get('mechanics', set())):s}\n"
               f"https://boardgamegeek.com/boardgame/{parameters.get('identity', ':question:'):s}\n"
               f">>>{parameters.get('description', ':question:'):s}")
    message = unescape(message)
    while "\n\n" in message:
        message = message.replace("\n\n", "\n")
    if len(message) > 4000:
        message = message[:3999] + "…"
    return message


@bot.on_command('bgg')
@loading_status
def handle_bgg(command: Command):
    """
    `!bgg board_game` - Gets the details of `board_game` from Board Game Geek
    """

    if not command.has_arg():
        raise UsageSyntaxException()
    argument = command.arg

    identity = get_bgg_id(argument)
    if identity is None:
        bot.post_message(command.channel_id, "Could not find board game with that name.")
        return

    parameters = get_board_game_parameters(identity)
    if parameters is None:
        bot.post_message(command.channel_id, "Something has gone wrong.")
        return

    message = format_board_game_parameters(parameters)
    bot.post_message(command.channel_id, message, unfurl_links=False, unfurl_media=False)
