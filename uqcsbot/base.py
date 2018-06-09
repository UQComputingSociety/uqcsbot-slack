from slackclient import SlackClient
from .api import APIWrapper, ChannelWrapper, Channel
from functools import partial
import collections
import asyncio
import concurrent.futures
import threading
import logging
import time
from contextlib import contextmanager
from typing import Callable, Optional, Union, TypeVar, DefaultDict, Type
from apscheduler.schedulers.background import BackgroundScheduler


CmdT = TypeVar('CmdT', bound='Command')


class Command(object):
    def __init__(self, command_name: str, arg: Optional[str], channel: Channel, message: dict) -> None:
        self.command_name = command_name
        self.channel = channel
        self.arg = arg
        self.message = message

    def has_arg(self) -> bool:
        return self.arg is not None

    @classmethod
    def from_message(cls: Type[CmdT], message: dict) -> Optional[CmdT]:
        text = message.get("text", '')
        if message.get("subtype") == "bot_message" or not text.startswith("!"):
            return None
        command_name, *arg = text[1:].split(" ", 1)
        return cls(
            command_name=command_name,
            channel=bot.channels.get(message["channel"]),
            arg=None if not arg else arg[0],
            message=message
        )

    @property
    def user_id(self):
        return self.message['user']


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


class UQCSBot(object):
    api_token: Optional[str] = underscored_getter("api_token")
    client: Optional[SlackClient] = underscored_getter("client")
    verification_token: Optional[str] = underscored_getter("verification_token")
    executor: Optional[concurrent.futures.ThreadPoolExecutor] = underscored_getter("executor")
    scheduler: Optional[BackgroundScheduler] = underscored_getter("scheduler")
    command_registry: Optional[DefaultDict[str, list]] = underscored_getter("command_registry")

    def __init__(self, logger=None):
        self._api_token = None
        self._client = None
        self._verification_token = None
        self._executor = concurrent.futures.ThreadPoolExecutor()
        self.logger = logger or logging.getLogger("uqcsbot")
        self._handlers = collections.defaultdict(list)
        self._command_registry = collections.defaultdict(list)
        self._scheduler = BackgroundScheduler()

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

    def on_command(self, command_name: str):
        def decorator(fn):
            self.command_registry[command_name].append(fn)
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
        self._handlers[message_type].append(handler_fn)
        return handler_fn

    def api_call(self, *args, **kwargs):
        self.client.api_call(*args, **kwargs)

    api_call.__doc__ = SlackClient.api_call.__doc__

    @property
    def api(self):
        """
        See uqcsbot.api.APIWrapper for usage information.
        """
        return APIWrapper(self.client)

    def post_message(self, channel: Union[Channel, str], text: str, **kwargs):
        channel_id = channel if isinstance(channel, str) else channel.id
        return self.api.chat.postMessage(channel=channel_id, text=text, **kwargs)

    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        """
        Provides an AbstractEventLoop that works in the current command context.

        This is the extent of our asyncio support.
        """
        policy = asyncio.get_event_loop_policy()
        if policy._local._loop is None:  # type: ignore
            policy.set_event_loop(policy.new_event_loop())
        return policy.get_event_loop()

    @contextmanager
    def _execution_context(self):
        """
        Starts the scheduler for timed tasks, and on error does cleanup
        """
        self._scheduler.start()
        try:
            yield
        except:
            self.logger.exception("An error occurred, exiting")
            self._scheduler.shutdown()
            self._executor.shutdown()
            raise

    def _execute_catching_error(self, handler, evt):
        """
        Wraps handler execution so that any errors that occur in a handler are
        logged and ignored.
        """
        try:
            return handler(evt)
        except Exception:
            self.logger.exception('Error in handler')
            return None

    def _handle_command(self, message: dict) -> None:
        """
        Run handlers for commands, wrapping messages in a `Command` object
        before passing them to the handler. Handlers are executed by a
        ThreadPoolExecutor.
        """
        command = Command.from_message(message)
        if command is None:
            return
        for handler in self.command_registry[command.command_name]:
            self.executor.submit(
                self._execute_catching_error,
                handler,
                command,
            )

    def _run_handlers(self, event: dict):
        """
        Run handlers for raw messages based on message type. Handlers are
        executed by a ThreadPoolExecutor.
        """
        self.logger.debug(f"Running handlers for {event}")
        if "type" not in event:
            self.logger.error(f"No type in message: {event}")
        handlers = self._handlers[event['type']] + self._handlers['']
        return [
            self.executor.submit(
                self._execute_catching_error,
                handler,
                event,
            )
            for handler in handlers
        ]

    def run(self, api_token, verification_token, **kwargs):
        """
        Run the bot.

        api_token: Slack API token
        verification_token: Events API verification token
        """
        self._api_token = api_token
        self._client = SlackClient(api_token)
        self._verification_token = verification_token
        with self._execution_context():
            # Initialise channels at start so we don't have to block
            self.channels._initialise()

            if not self.client.rtm_connect():
                raise OSError("Error connecting to RTM API")
            while True:
                for message in self.client.rtm_read():
                    self._run_handlers(message)
                    if message.get('type') == "goodbye":
                        break
                time.sleep(0.5)

    def run_cli(self):
        """
        Run in local (CLI) mode
        """

        def cli_api_call(method, **kwargs):
            if method == "chat.postMessage":
                print(kwargs['text'])
            else:
                print(kwargs)

        self.api_call = cli_api_call
        with self._execution_context():
            while True:
                response = input("> ")
                self._run_handlers({
                    "text": response,
                    "channel": "general",
                    "subtype": "user",
                    "type": "message"
                })


bot = UQCSBot()
