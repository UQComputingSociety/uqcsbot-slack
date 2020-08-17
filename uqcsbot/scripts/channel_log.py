from uqcsbot import bot


@bot.on("channel_created")
def channel_log(evt: dict):
    """
    Notes when channels are created in #uqcs-meta

    @no_help
    """
    bot.post_message(bot.channels.get("uqcs-meta"),
                     'New Channel Created: '
                     + f'<#{evt.get("channel").get("id")}|{evt.get("channel").get("name")}>')
