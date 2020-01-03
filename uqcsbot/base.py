import slack
from uqcsbot.api import APIWrapper, ChannelWrapper, Channel, UsersWrapper
from functools import partial, wraps
import collections
import asyncio
import concurrent.futures
import logging
import inspect
import threading
from contextlib import contextmanager
from typing import Callable, Optional, Union, TypeVar, DefaultDict, Type, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from uqcsbot.utils.command_utils import UsageSyntaxException, get_helper_doc
from unidecode import unidecode


CmdT = TypeVar('CmdT', bound='Command')


class Command(object):
    def __init__(self, name: str, arg: Optional[str], message: dict, thread_ts: Optional[int] = None, thread_bcast: bool = None) -> None:
        self.name = name
        self.arg = arg
        self.message = message
        self.thread_ts = thread_ts
        self.thread_bcast = thread_bcast

    def has_arg(self) -> bool:
        return self.arg is not None

    @classmethod
    def from_message(cls: Type[CmdT], message: dict) -> Optional[CmdT]:
        text = unidecode(message.get("text", ''))
        if message.get("subtype") == "bot_message" or not text.startswith("!"):
            return None
        name, *arg = text[1:].split(" ", 1)
        return cls(
            name=name,
            arg=None if not arg else arg[0],
            message=message,
            thread_ts=message.get('thread_ts'),
            thread_bcast=message.get("subtype") == "thread_broadcast",
        )

    @property
    def user_id(self):
        """
        Returns the id of the user who called the command.
        """
        return self.message['user']

    @property
    def channel_id(self):
        """
        Returns the id of the channel that the command was called in.
        """
        return self.message['channel']

    def reply_with(self, bot, response):
        if self.thread_bcast:
            bot.post_message(self.channel_id, response, reply_broadcast=True,
                             thread_ts=self.thread_ts)
        else:
            bot.post_message(self.channel_id, response, thread_ts=self.thread_ts)



CommandHandler = Callable[[Command], None]


def protected_property(prop_name: str, attr_name: str):
    """
    Makes a read-only getter called `prop_name` that gets `attr_name`
    """
    def prop_fn(self):
        return getattr(self, attr_name)
    prop_fn.__name__ = prop_name
    return property(prop_fn)


def underscored_getter(s: str) -> Any:
    return protected_property(s, '_' + s)


class ModifiedRTMClient(slack.RTMClient):
    def __init__(self, *, executor, handlers, **kwargs):
        super().__init__(**kwargs, connect_method='rtm.connect')
        self._executor = executor
        self._callbacks = handlers

    async def _dispatch_event(self, event: str, data=None):
        """
        Similar to the original implementation, but assumes that tasks never
        fail and sync code should always be run in a thread.
        """
        waiting = []
        # calling code does a .pop here
        if data is not None:
            data['type'] = event
        for callback in self._callbacks[event]:
            self._logger.debug(
                "Starting %s callbacks for event: '%s'",
                len(self._callbacks[event]),
                event,
            )
            if self._stopped and event not in ["close", "error"]:
                # Don't run callbacks if client was stopped unless they're
                # close/error callbacks.
                break

            if inspect.iscoroutinefunction(callback):
                waiting.append(asyncio.ensure_future(
                    callback(rtm_client=self, web_client=self._web_client, data=data)
                ))
            else:
                waiting.append(asyncio.ensure_future(
                    self._execute_in_thread(callback, data)
                ))
        for coro in waiting:
            await coro
    _dispatch_event.__doc__ = slack.RTMClient._dispatch_event.__doc__

    def _execute_in_thread(self, callback, data):
        return self._event_loop.run_in_executor(self._executor, callback, data)


class UQCSBot(object):
    user_token: Optional[str] = underscored_getter("user_token")
    bot_token: Optional[str] = underscored_getter("bot_token")
    bot_client: Optional[slack.WebClient] = underscored_getter("bot_client")
    user_client: Optional[slack.WebClient] = underscored_getter("user_client")
    rtm_client: Optional[slack.RTMClient] = underscored_getter("rtm_client")
    verification_token: Optional[str] = underscored_getter("verification_token")
    executor: concurrent.futures.ThreadPoolExecutor = underscored_getter("executor")

    def __init__(self, logger=None):
        self._user_token = None
        self._user_client = None
        self._bot_token = None
        self._bot_client = None
        self._verification_token = None
        self._executor = concurrent.futures.ThreadPoolExecutor()
        self.logger = logger or logging.getLogger("uqcsbot")
        self._handlers: DefaultDict[str, list] = collections.defaultdict(list)
        self._command_registry: DefaultDict[str, list] = collections.defaultdict(list)
        self._scheduler = AsyncIOScheduler()

        self.register_handler('message', self._handle_command)
        self.register_handler('hello', self._handle_hello)
        self.register_handler('goodbye', self._handle_goodbye)

        self.channels = ChannelWrapper(self)
        self.users = UsersWrapper(self)

    def _handle_hello(self, evt):
        if evt != {"type": "hello"}:
            self.logger.debug(f"Hello event has unexpected extras: {evt}")
        self.logger.info(f"Successfully connected to server")

    def _handle_goodbye(self, evt):
        if evt != {"type": "goodbye"}:
            self.logger.debug(f"Goodbye event has unexpected extras: {evt}")
        self.logger.info(f"Server is about to disconnect")

    def on_command(self, command_name: str):
        def decorator(command_fn):
            """
            Decorator function which returns a wrapper function that catches any
            UsageSyntaxExceptions and sends the wrapped command's helper doc to the calling channel.
            Also adds the function as a handler for the given command name.
            """
            @wraps(command_fn)
            def wrapper(command: Command):
                try:
                    return command_fn(command)
                except UsageSyntaxException:
                    helper_doc = get_helper_doc(command.name)
                    self.post_message(command.channel_id, f'usage: {helper_doc}')
            self._command_registry[command_name].append(wrapper)
            return wrapper
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

    def api_call(self, method, **kwargs):
        return getattr(self.api, method)(**kwargs)

    api_call.__doc__ = slack.WebClient.api_call.__doc__

    @property
    def api(self):
        """
        See uqcsbot.api.APIWrapper for usage information.
        """
        return APIWrapper(self.user_client, self.bot_client)

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
        self._loop = self.get_event_loop()
        current = threading.current_thread()
        og_run_until_complete = self._loop.run_until_complete

        def cooked_run_until_complete(fut):
            if threading.current_thread() == current:
                return og_run_until_complete(fut)
            else:
                evt = threading.Event()
                fut.add_done_callback(lambda *a: evt.set())
                evt.wait()
                return fut.result()
        self._loop.run_until_complete = cooked_run_until_complete

        self._user_client = slack.WebClient(token=self.user_token, loop=self._loop)
        self._bot_client = slack.WebClient(token=self.bot_token, loop=self._loop)

        self._scheduler.configure(event_loop=self._loop)
        self._scheduler.start()
        try:
            yield
        except Exception:
            self.logger.exception("An error occurred, exiting")
            raise
        finally:
            self._scheduler.shutdown()
            self._executor.shutdown()
            self._loop.close()

    def _execute_catching_error(self, handler, evt):
        """
        Wraps handler execution so that any errors that occur in a handler are
        logged and ignored.
        """
        try:
            return handler(evt)
        except Exception:
            self.logger.exception(f'Error in handler while processing {evt}')
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
        for handler in self._command_registry[command.name]:
            self.executor.submit(self._execute_catching_error, handler, command)

    async def _run_handlers(self, event: dict):
        """
        Run handlers for raw messages based on message type. Handlers are
        executed by a ThreadPoolExecutor.
        """
        self.logger.debug(f"Running handlers for {event}")
        if "type" not in event:
            self.logger.error(f"No type in message: {event}")
        handlers = self._handlers[event['type']] + self._handlers['']
        futures = [
            self._loop.run_in_executor(
                self.executor,
                self._execute_catching_error,
                handler,
                event
            ) for handler in handlers
        ]
        return [(await future) for future in futures]

    def run(self, user_token, bot_token):
        """
        Run the bot.

        api_token: Slack API token
        verification_token: Events API verification token
        """
        self._user_token = user_token
        self._bot_token = bot_token
        with self._execution_context():
            self._rtm_client = ModifiedRTMClient(
                token=self.bot_token,
                executor=self.executor,
                handlers=self._handlers,
                loop=self._loop,
            )
            try:
                self.rtm_client.start()
            except KeyboardInterrupt:
                self.rtm_client.stop()


bot = UQCSBot()
