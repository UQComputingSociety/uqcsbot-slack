import os
import sys
import importlib
from slackclient import SlackClient
from slackeventsapi import SlackEventAdapter
from uqcsbot.command_handler import CommandHandler
from uqcsbot.stub import ClientStub, EventAdapterStub
from uqcsbot.api import Bot

SLACK_VERIFICATION_TOKEN = os.environ.get("SLACK_VERIFICATION_TOKEN", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")

command_handler: CommandHandler = None
bot: Bot = None


def main():
    if '--dev' in sys.argv:
        client = ClientStub()
        event_adapter = EventAdapterStub()
    else:
        client = SlackClient(SLACK_BOT_TOKEN)
        event_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/uqcsbot/events")

    # this doesn't work
    global command_handler
    global bot
    command_handler = CommandHandler(client, event_adapter)
    bot = Bot(client)

    dir_path = os.path.dirname(__file__)
    scripts_dir = os.path.join(dir_path, 'scripts')
    for sub_file in os.listdir(scripts_dir):
        if not sub_file.endswith('.py') or sub_file == '__init__.py':
            continue
        module = f'uqcsbot.scripts.{sub_file[:-3]}'
        importlib.import_module(module)

    event_adapter.start(port=5000)

if __name__ == "__main__":
    main()
