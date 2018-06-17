from uqcsbot import bot, Command
from functools import partial
from uqcsbot.utils.command_utils import UsageSyntaxException


@bot.on_command('voteythumbs')
def handle_voteythumbs(command: Command):
    '''
    `!voteythumbs <TOPIC>` - Starts a :thumbsup: :thumbsdown: vote on the given
    topic. If unspecified, will not set a topic.
    '''
    if not command.has_arg():
        raise UsageSyntaxException()

    add_vote_react = partial(
        bot.api.reactions.add,
        channel=command.channel_id,
        timestamp=command.message['ts'],
    )

    for emoji in ["thumbsup", "thumbsdown", "eyes"]:
        add_vote_react(name=emoji)
