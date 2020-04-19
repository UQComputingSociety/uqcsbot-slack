from functools import partial
from uqcsbot import bot, Command


@bot.on_command('voteythumbs')
@bot.on_command('voteythimbs')
def handle_voteythumbs(command: Command):
    """
    `!voteythumbs [TOPIC]` - Starts a :thumbsup: :thumbsdown: :thumbsright: vote.
    `!voteythimbs [TOPIC]` - Starts a :thumbsup: :thumbsdown: :thumbsright: vote.
    """
    add_vote_react = partial(
        bot.api.reactions.add,
        channel=command.channel_id,
        timestamp=command.message['ts'],
    )

    for emoji in ["thumbsup", "thumbsdown", "thumbsright", "doublethumbsup"]:
        add_vote_react(name=emoji)
