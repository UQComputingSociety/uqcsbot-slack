from uqcsbot import bot
import logging


@bot.on('message')
def wavie(evt):
    """
    :wave: reacts to "person joined/left this channel"

    @no_help
    """
    if evt.get('subtype') not in ['channel_join', 'channel_leave']:
        return
    chan = bot.channels.get(evt['channel'])
    if chan is not None and chan.name == 'announcements':
        return
    bot.api.reactions.add(name='wave', channel=chan.id, timestamp=evt['ts'])
