from uqcsbot import bot, Command

repos = {
        "uqcsbot": "https://github.com/UQComputingSociety/uqcsbot",
        "desgin": "https://github.com/UQComputingSociety/design",
        "constitution": "https://github.com/UQComputingSociety/constitution",
        "signup": "https://github.com/UQComputingSociety/signup",
        "website": "https://github.com/UQComputingSociety/website",
        "inviter": "https://github.com/UQComputingSociety/slack-invite-automation",  # noqa
        "coc": "https://github.com/UQComputingSociety/code-of-conduct",
        "shirts": "https://github.com/UQComputingSociety/shirts",
        "events": "https://github.com/UQComputingSociety/events",
        "cookbook": "https://github.com/UQComputingSociety/cookbook",
        "minutes": "https://github.com/UQComputingSociety/minutes"
}


@bot.on_command("repo")
def handle_repo(command: Command):
    '''
    `!repo` - Returns the url for the uqcsbot repo.
    '''

    channel = bot.channels.get(command.channel_id)
    command_args = command.arg.split() if command.has_arg() else []

    is_full_output = False
    if '--list' in command_args:
        command_args.remove('--list')
        is_full_output = True
    if '-l' in command_args:
        command_args.remove('-l')
        is_full_output = True

    repo_strs = []
    if is_full_output:
        for k, v in repos.items():
            repo_strs.append(f"<{v}|{k}>")
    else:
        if len(command_args) == 0:
            repo_strs.append(f"<{repos['uqcsbot']}|uqcsbot>")
        else:
            for c in command_args:
                repo_strs.append(f"<{repos[c]}|{c}>")
    bot.post_message(channel, "Click the repo: " +
                              ", ".join(repo_strs))
    if not is_full_output:
        bot.post_message(channel, "_Note: the list is not complete, please " +
                                  "use -l/--list to print the full list")
