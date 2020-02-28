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
        emoji_name = evt["name"]
        added = f':{emoji_name}: (`:{emoji_name}:`)'

        bot.post_message(emoji_request, f'Emoji added: {added}')

    elif subtype == 'remove':
        names = evt.get("names")
        removed = ', '.join(f'`:{name}:`' for name in names)
        plural = 's' if len(names) > 1 else ''

        bot.post_message(emoji_request,
            f'Emoji{plural} removed: {removed}')
