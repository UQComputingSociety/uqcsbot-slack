from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
from typing import List, Optional


UQCS_REPO_URL = "https://github.com/UQComputingSociety/"

REPOS = {
    "coc": ("code-of-conduct", "The UQCS Code of Conduct to be followed by all community members"),
    "constitution": ("constitution", "All the business details"),
    "cookbook": ("cookbook", "A cookbook of recipes contributed by UQCS members"),
    "design": ("design", "All UQCS design assets"),
    "events": ("events", "A repository for events and talk materials"),
    "inviter": ("slack-invite-automation", "A tiny web application to invite a user to our slack team"),
    "minutes": ("minutes", "Minutes from UQCS committee meetings and general meetings"),
    "shirts": ("shirts", "A payment system to accept preorders of UQCS tshirts"),
    "signup": ("signup", "The UQCS membership signup system"),
    "uqcsbot": ("uqcsbot", "Our friendly little Slack bot"),
    "website": ("website", "The UQ Computing Society website"),
}


def format_repo_message(repos: Optional[List[str]]) -> str:
    """
    Takes a list of repo names and matches them to REPOS keys, constructing a message from the
    relevant repo information.
    :param repos: list of strings of repo names
    :return: a single string with a formatted message containing repo info for the given names
    """
    repo_strings = []
    for potential_repo in repos:
        if potential_repo not in REPOS.keys():
            repo_strings.append(f"> Unrecognised repo \"{potential_repo}\"\n")
        else:
            repo_strings.append(f"> • <{UQCS_REPO_URL + REPOS[potential_repo][0]}|*{potential_repo}*>:"
                                f" {REPOS[potential_repo][1]}\n")
    return "".join(repo_strings)


@bot.on_command("repo")
@loading_status
def handle_repo(command: Command):
    """
    `!repo` - Returns the url for the uqcsbot Github repository and other club repos
    """

    # Setup for message passing
    channel = bot.channels.get(command.channel_id)
    # Read the commands provided
    arguments = command.arg.split() if command.has_arg() else []

    # All repos
    if len(arguments) > 0 and arguments[0] in ["--list", "-l", "list", "full", "all"]:
        return bot.post_message(channel,
                                "_Useful :uqcs: Github repositories_:\n"
                                + format_repo_message(list(REPOS.keys())))

    # List of specific repos
    if len(arguments) > 0:
        return bot.post_message(channel,
                                "_Requested :uqcs: Github repositories_:\n"
                                + format_repo_message(arguments))

    # Default option: just uqcsbot link
    return bot.post_message(channel,
                            "_Have you considered contributing to the bot?_\n" +
                            format_repo_message(["uqcsbot"]) +
                            "\n _For more repositories, try_ `!repo list`")
