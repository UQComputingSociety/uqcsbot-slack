from uqcsbot import bot
from random import choice, sample

REACTS = ['waiting', 'apple_waiting', 'waiting_droid', 'keen', 'fiestaparrot']


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
    msg = await bot.run_async(bot.post_message, channel, '\r\n'.join(lines))
    bot.api.reactions.add(name=choice(REACTS), channel=channel.id, timestamp=msg['ts'])
