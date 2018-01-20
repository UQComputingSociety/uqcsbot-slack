from pyee import EventEmitter
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import os

SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/uqcsbot/events")
slack_client = SlackClient(SLACK_BOT_TOKEN)

class Command:
    def __init__(self, command_name, arg, channel):
        self.command_name = command_name
        self.arg = arg
        self.channel = channel
    
    def has_arg(self):
        return self.arg is not None

class CommandHandler(EventEmitter):
    def __init__(self, adapter):
        EventEmitter.__init__(self)
        adapter.on("message", self.handle_command)

    def handle_command(self, event_data):
        message = event_data["event"]
        if message.get("subtype") == "bot_message" or not message.get("text").startswith("!"):
            return
        command_name, *arg = message["text"][1:].split(" ", 1)
        command = Command(command_name, None if not arg else arg[0], message["channel"])
        self.emit(command_name, command)

class API:
    def __init__(self, client):
        self.client = client

    def post_Message(self, channel, text):
        self.client.api_call("chat.postMessage", channel=channel, text=text)

command_handler = CommandHandler(slack_events_adapter)
api = API(slack_client)

@command_handler.on("echo")
def handle_echo(command):
    if command.has_arg():
        api.post_Message(command.channel, command.arg)

slack_events_adapter.start(port=5000)