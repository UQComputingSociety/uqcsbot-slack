from pyee import EventEmitter
from uqcsbot.command_handler import CommandHandler

class ClientStub(object):
    def __init__(self, handler: CommandHandler):
        self.adapter = EventAdapterStub()
        self.adapter.on("message", handler.handle_command)

    def api_call(self, call: str, channel: str, text: str):
        if call == "chat.postMessage":
            print(text)

class EventAdapterStub(EventEmitter):
    def prompt(self):
        response = input("> ")
        message = {
            "event" : {
                "text" : response,
                "channel" : "general",
                "subtype" : "user"
            }
        }
        self.emit("message", message)
        self.prompt()