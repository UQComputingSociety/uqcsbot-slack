from uqcsbot import bot

MESSAGE = "_Ceterum autem censeo praeses capillum esse delendam_."


@bot.on("message")
def cato(event: dict):
    """
    Reminds the UQCS President of their duties
    """

    # respone only to the president
    if event.get("user") != "U9D6J8HB8":
        return

    # ensure message proper
    if "subtype" in event and event.get("subtype") != "thread_broadcast":
        return

    # post response
    if event.get("subtype") == "thread_broadcast":
        bot.post_message(event.get("channel"), MESSAGE, reply_broadcast=True,
                         thread_ts=event.get("thread_ts"))
    else:
        bot.post_message(event.get("channel"), MESSAGE, thread_ts=event.get("thread_ts"))
