from uqcsbot import bot, Command
from functools import partial


VOTEYTHUMBS_STRIP_PREFIXES = [
    '@channel',
    '@here',
    '@everyone',
    ':'  # intentionally last
]


def strip(message, prefixes=VOTEYTHUMBS_STRIP_PREFIXES):
    while True:
        # keep going until you didn't strip anything last pass
        for prefix in strip_from_start:
            if evt["text"].startswith(prefix):
                [len(prefix):].strip()
                break
    else:
        break
    return message


@bot.on('message')
async def voteythumbs(evt: dict):
    evt["text"] = strip(evt["text"])
    cmd = Command.from_message(bot, evt)
    cmd.arg = strip(cmd.arg)
    if not cmd.has_arg() and "!voteythumbs" in evt["text"]:
        await bot.run_async(bot.post_message, cmd.channel, "Invalid voteythumbs command")
    elif not cmd.has_arg():
        bot.logger.error("Invalid voteythumbs command")
        return

    result = await bot.run_async(bot.post_message, cmd.channel, "Starting vote: {cmd.arg}")
    add_reaction = lambda name: bot.run_async(
        bot.api.reactions.add,
        name=name,
        channel=cmd.channel.id,
        timestamp=result['ts'],
    )
    res = await add_reaction("thumbsup")
    if not res.get('ok'):
        bot.logger.error(f"Voteythumbs error adding \"thumbsup\": {res}")
        return
    await add_reaction("thumbsdown")
    if not res.get('ok'):
        bot.logger.error(f"Voteythumbs error adding \"thumbsdown\": {res}")
        return
    await add_reaction("eyes")
    if not res.get('ok'):
        bot.logger.error(f"Voteythumbs error adding \"eyes\": {res}")
