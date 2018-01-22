from pyee import EventEmitter
from slackclient import SlackClient
from slackeventsapi.server import SlackServer
from .api import Channel
import waitress
import collections
from typing import Callable


class Command(object):
    def __init__(self, command_name: str, arg: str, channel: Channel):
        self.command_name = command_name
        self.arg = arg
        self.channel = channel
    
    def has_arg(self) -> bool:
        return self.arg is not None


CommandHandler = Callable[[Command], None]


class UQCSBot(EventEmitter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_token = None
        self.client = None
        self.verification_token = None
        self.server = None
        self.on("message")(self._handle_command)
        self._command_registry = collections.defaultdict(list)

    def _handle_command(self, event_data: dict) -> None:
        message = event_data["event"]
        text = message.get("text")
        if message.get("subtype") == "bot_message" or text is None or not text.startswith("!"):
            return
        command_name, *arg = text[1:].split(" ", 1)
        channel = Channel(self.client, message["channel"])
        command = Command(command_name, None if not arg else arg[0], channel)
        for cmd in self._command_registry[command_name]:
            cmd(command)

    def on_command(self, command_name: str):
        def decorator(fn):
            self._command_registry[command_name].append(fn)
            return fn
        return decorator

    def api_call(self, *args, **kwargs):
        self.client.api_call(*args, **kwargs)

    api_call.__doc__ = SlackClient.api_call.__doc__

    def post_message(self, channel: Channel, text: str):
        self.api_call("chat.postMessage", channel=channel.id, text=text)

    def run(self, api_token, verification_token, **kwargs):
        """
        Run for realsies
        """
        self.api_token = api_token
        self.client = SlackClient(api_token)
        self.verification_token = verification_token
        self.server = SlackServer(verification_token, '/uqcsbot/events', self, None)
        waitress.serve(self.server, **kwargs)

    def run_debug(self):
        """
        Run in debug mode
        """
        def debug_api_call(method, **kwargs):
            if method == "chat.postMessage":
                print(kwargs['text'])
            else:
                print(kwargs)
        self.api_call = debug_api_call

        while True:
            response = input("> ")
            message = {
                "event": {
                    "text": response,
                    "channel": "general",
                    "subtype": "user"
                }
            }
            self.emit("message", message)


bot = UQCSBot()
