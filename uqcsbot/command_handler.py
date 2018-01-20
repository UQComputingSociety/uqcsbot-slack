from pyee import EventEmitter
from slackeventsapi import SlackEventAdapter


class Command(object):
    def __init__(self, command_name: str, arg: str, channel: str):
        self.command_name = command_name
        self.arg = arg
        self.channel = channel
    
    def has_arg(self) -> bool:
        return self.arg is not None


class CommandHandler(EventEmitter):
    def __init__(self, adapter: SlackEventAdapter):
        super().__init__()
        adapter.on("message", self.handle_command)

    def handle_command(self, event_data: dict):
        message = event_data["event"]
        if message.get("subtype") == "bot_message" or not message.get("text").startswith("!"):
            return
        command_name, *arg = message["text"][1:].split(" ", 1)
        command = Command(command_name, None if not arg else arg[0], message["channel"])
        self.emit(command_name, command)
