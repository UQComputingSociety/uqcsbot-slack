"""
Logs emoji addition/removal to emoji-request for audit purposes
"""
from uqcsbot import bot


@bot.on("emoji_changed")
def emoji_log(evt: dict):
    """
    Notes when emojis are added or deleted.

    @no_help
    """
    emoji_request = bot.channels.get("emoji-request")
    subtype = evt.get("subtype")

    if subtype == 'add':
        name = evt["name"]
        value = evt["value"]

        if value.startswith('alias:'):
            _, alias = value.split('alias:')

            bot.post_message(emoji_request,
                             f'Emoji alias added: `:{name}:` :arrow_right: `:{alias}:` (:{name}:)')

        else:
            bot.post_message(emoji_request, f'Emoji added: :{name}: (`:{name}:`)')

    elif subtype == 'remove':
        names = evt.get("names")
        removed = ', '.join(f'`:{name}:`' for name in names)
        plural = 's' if len(names) > 1 else ''

        bot.post_message(emoji_request, f'Emoji{plural} removed: {removed}')
