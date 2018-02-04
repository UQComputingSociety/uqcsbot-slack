from pyee import EventEmitter
from slackclient import SlackClient
from .api import Channel
from functools import partial
import waitress
import collections
import asyncio
import concurrent.futures
import threading
from contextlib import contextmanager
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


def async_worker(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


class UQCSBot(object):
    api_token: Optional[str] = underscored_getter("api_token")
    client: Optional[SlackClient] = underscored_getter("client")
    verification_token: Optional[str] = underscored_getter("verification_token")
    server: Optional[SlackServer] = underscored_getter("server")
    evt_loop: Optional[asyncio.AbstractEventLoop]
    executor: Optional[concurrent.futures.ThreadPoolExecutor]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_token = None
        self._client = None
        self._verification_token = None
        self._server = None
        self._evt_loop = asyncio.new_event_loop()
        self._executor = concurrent.futures.ThreadPoolExecutor()
        self._evt_loop.set_default_executor(self._executor)
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
            asyncio.run_coroutine_threadsafe(cmd(command), self._evt_loop)

    def on_command(self, command_name: str):
        def decorator(fn):
            if not asyncio.iscoroutinefunction(fn):
                fn = partial(self.run_async, fn)
            self._command_registry[command_name].append(fn)
            return fn
        return decorator

    def api_call(self, *args, **kwargs):
        self.client.api_call(*args, **kwargs)

    api_call.__doc__ = SlackClient.api_call.__doc__

    def post_message(self, channel: Channel, text: str):
        self.api_call("chat.postMessage", channel=channel.id, text=text)


    async def run_async(self, fn, *args, **kwargs):
        """
        Private:
        
        Runs a synchronous function in the bot's async executor, tracking it with
        asyncio.
        """
        return await self._evt_loop.run_in_executor(self._executor, partial(fn, *args, **kwargs))

    @contextmanager
    def _async_context(self):
        async_thread = threading.Thread(target=async_worker, args=(self._evt_loop,))
        async_thread.start()
        # Windows bugfix - cancelling queues requires a task being queued
        fix_future = asyncio.run_coroutine_threadsafe(asyncio.sleep(1000), self._evt_loop)
        try:
            yield
            fix_future.cancel()
        except:
            self._executor.shutdown()
            fix_future.cancel()
            self._evt_loop.stop()
            async_thread.join()
            self._evt_loop.close()
            raise

    def run(self, api_token, verification_token, **kwargs):
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
        with self._async_context():
            waitress.serve(self.server, **kwargs)

    def run_debug(self, evt_loop=None, executor=None):
        """
        Run in debug mode
        """
        self._evt_loop.set_debug(True)
        def debug_api_call(method, **kwargs):
            if method == "chat.postMessage":
                print(kwargs['text'])
            else:
                print(kwargs)

        self.api_call = debug_api_call
        with self._async_context():
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
