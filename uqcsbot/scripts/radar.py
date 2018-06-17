from uqcsbot import bot, Command
from time import time


@bot.on_command("radar")
def handle_radar(command: Command):
    '''
    `!radar` - Returns the latest BOM radar image for Brisbane.
    '''
    time_in_ms = int(round(time() * 1000))
    radar_url = f'https://bom.lambda.tools/?location=brisbane&_cache={time_in_ms}'
    bot.post_message(command.channel_id, radar_url)
