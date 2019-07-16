from uqcsbot import bot, Command

repos = {
    "coc": "https://github.com/UQComputingSociety/code-of-conduct",
    "constitution": "https://github.com/UQComputingSociety/constitution",
    "cookbook": "https://github.com/UQComputingSociety/cookbook",
    "desgin": "https://github.com/UQComputingSociety/design",
    "events": "https://github.com/UQComputingSociety/events",
    "inviter": "https://github.com/UQComputingSociety/slack-invite-automation",
    "minutes": "https://github.com/UQComputingSociety/minutes",
    "shirts": "https://github.com/UQComputingSociety/shirts",
    "signup": "https://github.com/UQComputingSociety/signup",
    "uqcsbot": "https://github.com/UQComputingSociety/uqcsbot",
    "website": "https://github.com/UQComputingSociety/website"
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
            repo_strs.append(f"<{v}|{k}>")
    else:
        # Add only the uqcsbot as the default result
        if len(command_args) == 0:
            repo_strs.append(f"<{repos['uqcsbot']}|uqcsbot>")
            if not is_list_output:
                bot.post_message(channel, "_Note: the list is not complete," +
                                          " please use -l/--list to print" +
                                          " the full list_")
        else:
            # Add each of the specified repos, don't prompt with -l
            for c in command_args:
                repo_strs.append(f"<{repos[c]}|{c}>")

    # Send the message to the channel
    bot.post_message(channel, "Click the link to go to to the repo: " +
                              ", ".join(repo_strs))
