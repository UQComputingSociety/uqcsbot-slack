from uqcsbot import bot
from random import choice, sample
from uqcsbot.scripts.loading_status import LOADING_REACTS

@bot.on_schedule('cron', hour=17, timezone='Australia/Brisbane')
async def wakie():
    '''
    'Wakes' up two UQCS members by pinging them on general and asking what
    they're working on.

    @no_help
    '''
    channel = bot.channels.get("general")
    victims = sample(channel.members, 2)
    lines = [f'Hey <@{v}>! Tell us about something cool you are working on!' for v in victims]
    wakie_message = await bot.as_async.post_message(channel, '\r\n'.join(lines))
    await bot.as_async.api.reactions.add(name=choice(LOADING_REACTS),
                                         channel=channel.id,
                                         timestamp=wakie_message['ts'])
