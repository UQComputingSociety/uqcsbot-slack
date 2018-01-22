from pyee import EventEmitter


class ClientStub(object):
    def api_call(self, method, **kwargs):
        if method == "chat.postMessage":
            print(kwargs['text'])


class EventAdapterStub(EventEmitter):
    def start(self):
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
