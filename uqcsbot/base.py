from slackclient import SlackClient
from .api import APIWrapper, ChannelWrapper, Channel
from functools import partial
import collections
import asyncio
import concurrent.futures
import threading
import logging
from contextlib import contextmanager
from typing import Callable, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler


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
    evt_loop: Optional[asyncio.AbstractEventLoop] = underscored_getter("evt_loop")
    executor: Optional[concurrent.futures.ThreadPoolExecutor] = underscored_getter("executor")
    scheduler: Optional[AsyncIOScheduler] = underscored_getter("scheduler")

    def __init__(self, logger=None):
        self._api_token = None
        self._client = None
        self._verification_token = None
        self._evt_loop = asyncio.new_event_loop()
        self._executor = concurrent.futures.ThreadPoolExecutor()
        self._evt_loop.set_default_executor(self._executor)
        self.logger = logger or logging.getLogger("uqcsbot")
        self._handlers = collections.defaultdict(list)
        self._command_registry = collections.defaultdict(list)
        self._scheduler = AsyncIOScheduler(event_loop=self._evt_loop)

        self.register_handler('message', self._handle_command)
        self.register_handler('hello', self._handle_hello)
        self.register_handler('goodbye', self._handle_goodbye)

        self.channels = ChannelWrapper(self)

    def _handle_hello(self, evt):
        if evt != {"type": "hello"}:
            self.logger.debug(f"Hello event has unexpected extras: {evt}")
        self.logger.info(f"Successfully connected to server")

    def _handle_goodbye(self, evt):
        if evt != {"type": "goodbye"}:
            self.logger.debug(f"Goodbye event has unexpected extras: {evt}")
        self.logger.info(f"Server is about to disconnect")

    async def _handle_command(self, message: dict) -> None:
        text = message.get("text")
        if message.get("subtype") == "bot_message" or text is None or not text.startswith("!"):
            return
        command_name, *arg = text[1:].split(" ", 1)
        channel = self.channels.get(message["channel"])
        command = Command(command_name, None if not arg else arg[0], channel)
        await asyncio.gather(*[
            self._await_error(cmd(command))
            for cmd in self._command_registry[command_name]
        ])

    def on_command(self, command_name: str):
        def decorator(fn):
            fn = self._wrap_async(fn)
            self._command_registry[command_name].append(fn)
            return fn
        return decorator

    def on(self, message_type: Optional[str], fn: Optional[Callable] = None):
        if fn is None:
            return partial(self.register_handler, message_type)
        return self.register_handler(message_type, fn)

    def on_schedule(self, *args, **kwargs):
        return lambda f: self._scheduler.add_job(f, *args, **kwargs)
    
    def register_handler(self, message_type: Optional[str], handler_fn: Callable):
        if message_type is None:
            message_type = ""
        if not callable(handler_fn):
            raise TypeError(f"Handler function {handler_fn} must be callable")
        handler_fn = self._wrap_async(handler_fn)
        self._handlers[message_type].append(handler_fn)
        return handler_fn

    def api_call(self, *args, **kwargs):
        self.client.api_call(*args, **kwargs)

    api_call.__doc__ = SlackClient.api_call.__doc__

    @property
    def api(self):
        return APIWrapper(self.client)

    def post_message(self, channel: Channel, text: str):
        self.api.chat.postMessage(channel=channel.id, text=text)

    def _wrap_async(self, fn):
        """
        Wrap a function to run it asynchronously if it's not already a coroutine function
        """
        if not asyncio.iscoroutinefunction(fn):
            fn = partial(self.run_async, fn)
        return fn

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
        self._scheduler.start()
        # Windows bugfix - cancelling queues requires a task being queued
        fix_future = asyncio.run_coroutine_threadsafe(asyncio.sleep(1000), self._evt_loop)
        try:
            yield
            fix_future.cancel()
        except:
            self.logger.exception("An error occurred, exiting")
            self._scheduler.shutdown()
            self._executor.shutdown()
            fix_future.cancel()
            self._evt_loop.stop()
            async_thread.join()
            self._evt_loop.close()
            raise

    async def _await_error(self, awaitable):
        try:
            return (await awaitable)
        except Exception:
            self.logger.exception('Error in handler')
            return None

    def _run_handlers(self, event):
        if "type" not in event:
            self.logger.error(f"No type in message: {event}")
        handlers = self._handlers[event['type']] + self._handlers['']
        awaitables = [
            asyncio.run_coroutine_threadsafe(
                self._await_error(handler(event)),
                loop=self.evt_loop
            )
            for handler in handlers
        ]

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
            if not self.client.rtm_connect():
                raise OSError("Error connecting to RTM API")
            while True:
                for message in self.client.rtm_read():
                    self._run_handlers(message)
                    if message.get('type') == "goodbye":
                        break

    def run_debug(self):
        """
        Run in debug mode
        """
        self.evt_loop.set_debug(True)

        def debug_api_call(method, **kwargs):
            if method == "chat.postMessage":
                print(kwargs['text'])
            else:
                print(kwargs)

        self.api_call = debug_api_call
        with self._async_context():
            while True:
                response = input("> ")
                self._run_handlers({
                    "text": response,
                    "channel": "general",
                    "subtype": "user",
                    "type": "message"
                })


bot = UQCSBot()
