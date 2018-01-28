from pyee import EventEmitter
from slackclient import SlackClient
from slackeventsapi.server import SlackServer
from .api import Channel
from functools import partial
import waitress
import collections
import asyncio
import concurrent.futures
import threading
from typing import Callable, Optional


class Command(object):
    def __init__(self, command_name: str, arg: str, channel: Channel):
        self.command_name = command_name
        self.arg = arg
        self.channel = channel
    
    def has_arg(self) -> bool:
        return self.arg is not None


CommandHandler = Callable[[Command], None]


def protected_property(prop_name, attr_name):
    """
    Makes a read-only getter called `prop_name` that gets `attr_name`
    """
    def prop_fn(self):
        return getattr(self, attr_name)
    prop_fn.__name__ = prop_name
    return property(prop_fn)
underscored_getter = lambda s: protected_property(s, '_' + s)


class UQCSBot(EventEmitter):
    api_token: Optional[str]
    client: Optional[SlackClient]
    verification_token: Optional[str]
    server: Optional[SlackServer]
    evt_loop: Optional[asyncio.AbstractEventLoop]
    executor: Optional[concurrent.futures.ThreadPoolExecutor]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_token = None
        self._client = None
        self._verification_token = None
        self._server = None
        self._evt_loop = None
        self._executor = None
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
            asyncio.ensure_future(cmd(command), loop=self.evt_loop)

    def on_command(self, command_name: str):
        def decorator(fn):
            if not asyncio.iscoroutinefunction(fn):
                fn = partial(self._run_function_async, fn)
            self._command_registry[command_name].append(fn)
            return fn
        return decorator

    def api_call(self, *args, **kwargs):
        self.client.api_call(*args, **kwargs)

    api_call.__doc__ = SlackClient.api_call.__doc__

    def post_message(self, channel: Channel, text: str):
        self.api_call("chat.postMessage", channel=channel.id, text=text)

    api_token = underscored_getter("api_token")
    client = underscored_getter("client")
    verification_token = underscored_getter("verification_token")
    server = underscored_getter("server")
    evt_loop = underscored_getter("evt_loop")
    executor = underscored_getter("executor")

    def _run_function_async(self, fn, *args, **kwargs):
        """
        Private:
        
        Runs a synchronous function in the bot's async executor, tracking it with
        asyncio.
        """
        return self.evt_loop.run_in_executor(self.executor, partial(fn, *args, **kwargs))

    def _setup_async(self, evt_loop=None, executor=None):
        if evt_loop is None:
            evt_loop = asyncio.get_event_loop()
        self._evt_loop = evt_loop

        if executor is None:
            executor = concurrent.futures.ThreadPoolExecutor()
        self._executor = executor

    def run(self, api_token, verification_token, evt_loop=None, executor=None, **kwargs):
        """
        Run the bot.

        api_token: Slack API token
        verification_token: Events API verification token
        evt_loop: asyncio event loop - if not provided uses default policy
        executor:
            Asynchronous executor - if not provided creates a ThreadPoolExecutor
        """
        self._api_token = api_token
        self._client = SlackClient(api_token)
        self._verification_token = verification_token
        self._server = SlackServer(verification_token, '/uqcsbot/events', self, None)
        self._setup_async(evt_loop, executor)
        def ws_worker():
            try:
                waitress.serve(self.server, **kwargs)
            except:
                self.executor.shutdown()
                self.evt_loop.stop()
                raise
        ws_thread = threading.Thread(target=ws_worker)
        ws_thread.start()
        self.evt_loop.run_forever()
        ws_thread.join()

    def run_debug(self, evt_loop=None, executor=None):
        """
        Run in debug mode
        """
        def debug_api_call(method, **kwargs):
            if method == "chat.postMessage":
                print(kwargs['text'])
            else:
                print(kwargs)
        def debug_worker():
            try:
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
            except:
                self.executor.shutdown()
                self.evt_loop.stop()
                raise

        self.api_call = debug_api_call
        self._setup_async(evt_loop, executor)
        self.evt_loop.set_debug(True)

        worker_thread = threading.Thread(target=debug_worker)
        worker_thread.start()

        self.evt_loop.run_forever()
        worker_thread.join()



bot = UQCSBot()
