from uqcsbot import bot
import logging


logger = logging.getLogger(__name__)


@bot.on('message')
def wave(evt):
    """
    Wave reacts to "person joined/left this channel"
    """
    if evt.get('subtype') not in ['channel_join', 'channel_leave']:
        return
    chan = bot.channels.get(evt['channel'])
    if chan is not None and chan.name == 'announcements':
        return
    result = bot.api.reactions.add(
        name='wave',
        channel=chan.id,
        timestamp=evt['ts'],
    )
    if not result.get('ok'):
        logger.error(f"Error adding reaction: {result}")
