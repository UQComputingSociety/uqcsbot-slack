from pyee import EventEmitter
from slackclient import SlackClient
from slackeventsapi import SlackEventAdapter
from uqcsbot.api import Channel


class Command(object):
    def __init__(self, command_name: str, arg: str, channel: Channel):
        self.command_name = command_name
        self.arg = arg
        self.channel = channel
    
    def has_arg(self) -> bool:
        return self.arg is not None


class CommandHandler(EventEmitter):
    def __init__(self, client: SlackClient, adapter: SlackEventAdapter):
        super().__init__()
        self.client = client
        adapter.on("message", self.handle_command)

    def handle_command(self, event_data: dict):
        message = event_data["event"]
        text = message.get("text")
        if message.get("subtype") == "bot_message" or text is None or not text.startswith("!"):
            return
        command_name, *arg = text[1:].split(" ", 1)
        channel = Channel(self.client, message["channel"])
        command = Command(command_name, None if not arg else arg[0], channel)
        self.emit(command_name, command)
