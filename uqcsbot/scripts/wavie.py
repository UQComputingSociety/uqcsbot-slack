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
    channel = bot.client.server.channels.find(evt['channel'])
    if channel.name == 'announcements':
        return
    result = bot.api.reactions.add(
        name='wave',
        channel=evt['channel'],
        timestamp=evt['ts'],
    )
    if not result.get('ok'):
        logger.error(f"Error adding reaction: {result}")