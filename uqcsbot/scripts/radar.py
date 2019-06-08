from uqcsbot import bot, Command
from time import time


@bot.on_command("radar")
def handle_radar(command: Command):
    """
    `!radar` - Returns the latest BOM radar image for Brisbane.
    """
    time_in_s = int(time())
    radar_url = f'https://bom.lambda.tools/?location=brisbane&timestamp={time_in_s}'
    attachment = {"image_url": radar_url, "text": None,
                  "fallback": "Screenshot from the Bureau of Meterology's Brisbane radar."}
    bot.post_message(command.channel_id, radar_url, attachments=[attachment])
