from requests import get
from xml.etree.ElementTree import fromstring
from difflib import SequenceMatcher
from html import unescape

from typing import Dict, Optional, Any

from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import UsageSyntaxException, loading_status

MAX_MESSAGE_LENGTH = 1500


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
    for item in results:
        if item.get("id") is None:
            continue
        for element in item:
            if element.tag == "name":
                match[item.get("id")] = SequenceMatcher(None, search_name,
                                                        element.get("value")).ratio()
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

    for element in result:
        tag = element.tag
        tag_name = element.attrib.get("name")
        tag_value = element.attrib.get("value")
        tag_type = element.attrib.get("type")
        tag_text = element.text

        # sets the range of players
        if tag == "poll" and tag_name == "suggested_numplayers":
            players = set()
            for option in element:
                numplayers = option.attrib.get("numplayers")
                votes = 0

                for result in option:
                    numvotes = int(result.attrib.get("numvotes"))
                    direction = -1 if result.attrib.get("value") == "Not Recommended" else 1
                    votes += numvotes * direction

                if votes > 0:
                    try:
                        players.add(int(numplayers))
                    except ValueError:
                        pass

            if players:
                parameters["min_players"] = min(players)
                parameters["max_players"] = max(players)

        # sets the name of the board game
        elif tag == "name" and tag_type == "primary":
            parameters["name"] = tag_value

        # adds a category
        elif tag == "link" and tag_type == "boardgamecategory":
            parameters["categories"].add(tag_value)

        # adds a mechanic
        elif tag == "link" and tag_type == "boardgamemechanic":
            parameters["mechanics"].add(tag_value)

        # sets the user ratings
        elif tag == "statistics":
            for statistic in element[0]:
                stat_tag = statistic.tag
                stat_value = statistic.attrib.get("value")
                if stat_tag == "average":
                    try:
                        parameters["score"] = str(round(float(stat_value), 2))
                    except ValueError:
                        parameters["score"] = stat_value
                if stat_tag == "usersrated":
                    parameters["users"] = stat_value
                if stat_tag == "ranks":
                    for genre in statistic:
                        genre_name = genre.attrib.get("name")
                        genre_value = genre.attrib.get("value")
                        if genre_name == "boardgame" and genre_value.isnumeric():
                            position = int(genre_value)
                            # gets the ordinal suffix
                            suffix = "tsnrhtdd"[(position/10 % 10 != 1) *
                                                (position % 10 < 4) * position % 10::4]
                            parameters["rank"] = f"{position:d}{suffix:s}"
                        elif genre_value.isnumeric():
                            friendlyname = genre.attrib.get("friendlyname")
                            # removes "game" as last word
                            friendlyname = " ".join(friendlyname.split(" ")[:-1])
                            position = int(genre_value)
                            # gets the ordinal suffix
                            suffix = "tsnrhtdd"[(position/10 % 10 != 1) *
                                                (position % 10 < 4) * position % 10::4]
                            parameters["subranks"][friendlyname] = f"{position:d}{suffix:s}"

        # sets the discription
        elif tag == "description":
            parameters["description"] = tag_text
        # sets the minimum playing time
        elif tag == "minplaytime":
            parameters["min_time"] = tag_value
        elif tag == "maxplaytime":
            parameters["max_time"] = tag_value

    return parameters


def format_board_game_parameters(parameters: dict) -> str:
    message = (f"*<https://boardgamegeek.com/boardgame/{parameters.get('identity'):s}"
               + f"|{parameters.get('name', ':question:'):s}>*\n"
               f"A board game for {parameters.get('min_players', ':question:'):d} to"
               + f" {parameters.get('max_players', ':question:'):d} players, with a"
               + f" playing time of {parameters.get('min_time', ':question:'):s} minutes"
               + ("" if parameters.get('min_time') == parameters.get('max_time')
                  else f" to {parameters.get('max_time', ':question:'):s} minutes") + ".\n"
               f"Rated {parameters.get('score', ':question:'):s}/10 by"
               + f" {parameters.get('users', ':question:'):s} users.\n"
               f"Ranked {parameters.get('rank', ':question:'):s} overall on _Board Game Geek_.\n"
               + "".join(f"• Ranked {value:s} in the {key:s} genre.\n"
                         for key, value in parameters.get("subranks", {}).items()) +
               f"Categories: {', '.join(parameters.get('categories', set())):s}\n"
               f"Mechanics: {', '.join(parameters.get('mechanics', set())):s}\n"
               f">>>{parameters.get('description', ':question:'):s}")
    message = unescape(message)
    while "\n\n" in message:
        message = message.replace("\n\n", "\n")
    
    if len(message) > MAX_MESSAGE_LENGTH:
        read_more = ("…\n\t\t<https://boardgamegeek.com/boardgame/"
                     + f"{parameters.get('identity'):s}|[read more]>")
        message = message[:MAX_MESSAGE_LENGTH-len(read_more)] + read_more
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
