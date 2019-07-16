from uqcsbot import bot, Command

UQCS_REPO_URL = "https://github.com/UQComputingSociety/"

repos = {
    "coc": "code-of-conduct",
    "constitution": "constitution",
    "cookbook": "cookbook",
    "desgin": "design",
    "events": "events",
    "inviter": "slack-invite-automation",
    "minutes": "minutes",
    "shirts": "shirts",
    "signup": "signup",
    "uqcsbot": "uqcsbot",
    "website": "website"
}


@bot.on_command("repo")
def handle_repo(command: Command):
    """
    `!repo` - Returns the url for the uqcsbot repo.
    """
    # Setup for message passing
    channel = bot.channels.get(command.channel_id)
    # Read the commands provided
    command_args = command.arg.split() if command.has_arg() else []

    # Checks for the list command
    is_list_output = False
    if '--list' in command_args:
        command_args.remove('--list')
        is_list_output = True
    if '-l' in command_args:
        command_args.remove('-l')
        is_list_output = True

    # Setup the empty list of formatted repo strings
    repo_strs = []
    if is_list_output:
        # Add all repos formatted as links
        for k, v in repos.items():
            repo_strs.append(f"<{UQCS_REPO_URL + v}|{k}>")
    else:
        # Add only the uqcsbot as the default result
        if len(command_args) == 0:
            repo_strs.append(f"<{UQCS_REPO_URL + repos['uqcsbot']}|uqcsbot>")
        else:
            # Add each of the specified repos to be printed
            for c in command_args:
                repo_strs.append(f"<{UQCS_REPO_URL + repos[c]}|{c}>")

    # Send the message to the channel
    bot.post_message(channel, "Click the link to go to to the repo: " +
                              ", ".join(repo_strs))

    # Prompt for a complete list if they did not specify a repo or list
    if not is_list_output and len(command_args) == 0:
        bot.post_message(channel, "_Note: the list is not complete, please " +
                                  "use -l/--list to print the full list_")
