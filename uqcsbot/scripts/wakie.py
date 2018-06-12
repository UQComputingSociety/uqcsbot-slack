from uqcsbot import bot
from random import choice, sample
from uqcsbot.util.status_reacts import LOADING_REACTS, HYPE_REACTS

@bot.on_schedule('cron', hour=17, timezone='Australia/Brisbane')
def wakie():
    '''
    'Wakes' up two UQCS members by pinging them on general and asking what
    they're working on.

    @no_help
    '''
    channel = bot.channels.get("general")
    victims = sample(channel.members, 2)
    lines = [f'Hey <@{v}>! Tell us about something cool you are working on!' for v in victims]
    wakie_message = bot.post_message(channel, '\r\n'.join(lines))
    bot.api.reactions.add(name=choice(HYPE_REACTS + LOADING_REACTS),
                                         channel=channel.id,
                                         timestamp=wakie_message['ts'])
