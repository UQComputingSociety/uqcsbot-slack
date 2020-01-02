from functools import partial
import time
import slack
import slack.errors
import threading
import logging
from typing import (TYPE_CHECKING, List, Iterable, Optional, Generator,
                    Any, Union, TypeVar, Dict, Type)
from typing_extensions import Literal
if TYPE_CHECKING:
    from uqcsbot.base import UQCSBot  # noqa

T = TypeVar('T')
ChanT = TypeVar('ChanT', bound='Channel')
UserT = TypeVar('UserT', bound='User')

LOGGER = logging.getLogger(__name__)

# This is used to track which client is preferred for a given method
_CLIENT_METHOD_REGISTRY: Dict[str, Union[Literal['bot'], Literal['user']]] = {
    'chat.postMessage': 'bot',
    'rtm.connect': 'user',
    'rtm.start': 'user',
}


class Paginator(Iterable[dict]):
    """
    Provides synchronous and asynchronous iterators over the
    pages of responses from a cursor-based paginated Slack

    See https://api.slack.com/docs/pagination for details
    """
    def __init__(self, caller: 'APIMethodProxy', **kwargs):
        self._kwargs = kwargs
        self._caller = caller

    def _gen(self) -> Generator[dict, Any, None]:
        kwargs = self._kwargs.copy()
        while True:
            page = self._caller(**kwargs)
            yield page
            cursor = page.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break
            kwargs["cursor"] = cursor

    def __iter__(self):
        return self._gen()


class APIMethodProxy(object):
    """
    Helper class used to implement APIWrapper
    """
    def __init__(self,  user_client: slack.WebClient, bot_client: slack.WebClient, method: str) -> None:
        self._user_client = user_client
        self._bot_client = bot_client
        self._method = method

    def __call__(self, **kwargs) -> dict:
        """
        Perform the relevant API request. Equivalent to SlackClient.api_call
        except the `method` argument is filled in.

        Attempts to retry the API call if rate-limited.
        """
        get_fn = lambda c: partial(
            getattr(
                getattr(self, f'_{c}_client'),
                self._method.replace('.', '_')
            ),
            **kwargs
        )
        retry_count = 0
        call_type = _CLIENT_METHOD_REGISTRY.get(self._method, 'bot')
        while retry_count < 5:
            try:
                result = get_fn(call_type)()
            except slack.errors.SlackApiError as e:
                result = e.response
            if not result['ok'] and result['error'] == 'ratelimited':
                retry_after_secs = int(result['headers']['Retry-After'])
                LOGGER.info(f'Rate limited, retrying in {retry_after_secs} seconds')
                time.sleep(retry_after_secs)
                retry_count += 1
            elif not result['ok'] and result['error'] == 'not_allowed_token_type':
                call_type = {'bot': 'user', 'user': 'bot'}[call_type]
                retry_count += 1
            else:
                _CLIENT_METHOD_REGISTRY[self._method] = call_type
                break
        else:
            result = {'ok': False, 'error': 'Reached max rate-limiting retries'}
        if not result['ok']:
            LOGGER.error(f'Slack API error calling {self._method} with'
                         f' kwargs {kwargs}: {result["error"]}')
        return result

    def paginate(self, **kwargs) -> Paginator:
        """
        Returns a `Paginator` which allows you to iterate over each page of response data
        from a Slack response that is paginated in the cursor-style.

        Count/oldest/latest and page/count methods require manual pagination.
        """
        return Paginator(self, **kwargs)

    def __getattr__(self, item) -> 'APIMethodProxy':
        """
        Gets another APIMethodProxy with the same configuration as the current
        one, except the attribute that you tried to get is appended to the
        method of the source APIMethodProxy, with a dot separating them.

        For example,
            > APIMethodProxy("chat").postMessage
        is equivalent to
            > APIMethodProxy("chat.postMessage")
        """
        return APIMethodProxy(
            user_client=self._user_client,
            bot_client=self._bot_client,
            method=f'{self._method}.{item}',
        )


class APIWrapper(object):
    """
    Wraps the Slack API client to make it possible to use dotted methods.
    Can perform API requests both synchronously and asynchronously.

    Example usage:
        > api = APIWrapper(client)
        > api.chat.postMessage(channel="general", text="message")
    """
    def __init__(self, user_client: slack.WebClient, bot_client: slack.WebClient) -> None:
        self._user_client = user_client
        self._bot_client = bot_client

    def __getattr__(self, item) -> APIMethodProxy:
        return APIMethodProxy(
            user_client=self._user_client,
            bot_client=self._bot_client,
            method=item
        )

    def __repr__(self) -> str:
        return f"<APIWrapper of {repr(self._client)}>"


class Channel(object):
    def __init__(self, bot: 'UQCSBot',
                 channel_id: str,
                 name: str,
                 is_group: bool = False,
                 is_im: bool = False,
                 is_public: bool = False,
                 is_private: bool = False,
                 is_archived: bool = False,
                 previous_names: List[str] = None) -> None:
        self._bot = bot
        self.id = channel_id
        self.name = name
        self._member_ids = None  # type: Optional[List[str]]
        self.is_group = is_group
        self.is_im = is_im
        self.is_public = is_public
        self.is_private = is_private
        self.is_archived = is_archived
        self.previous_names = previous_names or []
        self._lock = threading.Lock()

    def load_members(self):
        if self._member_ids is not None:
            # Quick exit without lock
            return
        with self._lock:
            if self._member_ids is not None:
                # Quick exit with lock
                return
            self._bot.logger.debug(f"Loading members for {self.name}<{self.id}>")
            members_ids = []  # type: List[str]
            for page in self._bot.api.conversations.members.paginate(channel=self.id):
                members_ids += page.get("members", [])
            self._member_ids = members_ids

    @property
    def members(self) -> List[str]:
        if self._member_ids is None:
            self.load_members()
        return self._member_ids  # type: ignore

    @classmethod
    def from_dict(cls: Type[ChanT], bot, chan_dict: dict) -> ChanT:
        chan = cls(bot=bot,
                   channel_id=chan_dict['id'],
                   name=chan_dict['name'],
                   is_group=chan_dict.get('is_group', False),
                   is_im=chan_dict.get('is_im', False),
                   is_public=chan_dict.get('is_public', False),
                   is_private=chan_dict.get('is_private', False),
                   is_archived=chan_dict.get('is_archived', False))
        return chan


class ChannelWrapper(object):
    def __init__(self, bot: 'UQCSBot') -> None:
        self._bot = bot
        self._initialised = False
        self._channels_by_id = {}  # type: Dict[str, Channel]
        self._channels_by_name = {}  # type: Dict[str, Channel]
        self._lock = threading.RLock()
        self._bind_handlers()

    def _bind_handlers(self) -> None:
        PREFIX = "_on_"
        for name in dir(type(self)):
            if not name.startswith(PREFIX):
                continue
            attr = getattr(self, name)
            mtype = name[len(PREFIX):]
            self._bot.on(mtype, attr)

    def _add_channel(self, chan_dict: dict) -> Channel:
        chan = Channel.from_dict(self._bot, chan_dict)
        self._channels_by_name[chan.name] = chan
        self._channels_by_id[chan.id] = chan
        return chan

    def _initialise(self):
        with self._lock:
            if self._initialised:
                # Prevent double-calls after lock release
                return
            self._initialised = True
            self._channels_by_id = {}
            self._channels_by_name = {}
            for page in self._bot.api.conversations.list.paginate(exclude_members='true', types="public_channel,private_channel,mpim,im"):
                for chan in page['channels']:
                    if chan["is_im"]:
                        if chan['is_user_deleted']:
                            continue
                        # Set the channel name to the user being directly messaged
                        # for easier reverse lookups. Note: `user` here is the user_id.
                        chan['name'] = chan['user']
                    self._add_channel(chan)
            self._initialised = True

    def populate_from_team_state(self, data):
        with self._lock:
            self._initialised = True
            self._channels_by_id = {}
            self._channels_by_name = {}
            loaded_so_far = 0
            for ctype in ['channels', 'groups', 'ims']:
                for chan in data[ctype]:
                    if ctype == 'ims':
                        # Set the channel name to the user being directly messaged
                        # for easier reverse lookups. Note: `user` here is the user_id.
                        chan['name'] = chan['user']
                    self._add_channel(chan)
                self._bot.logger.info(
                    f"Loaded {len(self._channels_by_id) - loaded_so_far} {ctype} from team state"
                )
                loaded_so_far = len(self._channels_by_id)

    def reload(self):
        self._initialised = False
        self._initialise()

    def get(self, name_or_id: str, default: Optional[T] = None,
            use_cache: bool = True) -> Union[Channel, Optional[T]]:
        if use_cache and not self._initialised:
            self._initialise()
        if name_or_id in self._channels_by_id:
            return self._channels_by_id[name_or_id]
        elif name_or_id in self._channels_by_name:
            return self._channels_by_name[name_or_id]
        elif not use_cache:
            resp = self._bot.api.channels.info(channel=name_or_id)
            if not resp.get('ok'):
                return default
            with self._lock:
                return self._add_channel(resp['channel'])
        else:
            return default

    def __iter__(self):
        return iter(self._channels_by_id.values())

    def _on_im_created(self, evt):
        chan = evt['channel']
        # Set the channel name to the user being directly messaged for easier
        # reverse lookups. Note: `user` here is the user_id.
        chan['name'] = evt['user']
        self._add_channel(chan)

    def _on_member_joined_channel(self, evt):
        chan = self.get(evt['channel'])
        # Load members if we haven't already before locking to prevent deadlock.
        chan.load_members()
        with chan._lock:
            members = chan.members
            user = evt['user']
            if user not in members:
                members.append(user)

    def _on_member_left_channel(self, evt):
        chan = self.get(evt['channel'])
        # Load members if we haven't already before locking to prevent deadlock.
        chan.load_members()
        with chan._lock:
            members = chan.members
            user = evt['user']
            if user in members:
                members.remove(user)

    def _on_channel_rename(self, evt):
        with self._lock:
            chan = self.get(evt['channel']['id'])
            self._channels_by_name.pop(chan.name)
            new_channel_name = evt['channel']['name']
            chan.name = new_channel_name
            self._channels_by_name[chan.name] = new_channel_name

    def _on_channel_archive(self, evt):
        chan = self.get(evt['channel'])
        chan.is_archived = True

    def _on_channel_unarchive(self, evt):
        chan = self.get(evt['channel'])
        chan.is_archived = False

    def _on_channel_created(self, evt):
        self._add_channel(evt["channel"])

    def _on_channel_deleted(self, evt):
        with self._lock:
            chan = self.get(evt['channel']['id'])
            self._channels_by_id.pop(chan.id)
            self._channels_by_name.pop(chan.name)

    def _on_group_rename(self, evt):
        self._on_channel_rename(evt)

    def _on_group_archive(self, evt):
        self._on_channel_archive(evt)

    def _on_group_unarchive(self, evt):
        self._on_channel_unarchive(evt)

    def _on_group_joined(self, evt):
        self._on_channel_created(evt)

    def _on_group_left(self, evt):
        self._on_channel_deleted(evt)


class UsersWrapper(object):
    def __init__(self, bot: 'UQCSBot') -> None:
        self._bot = bot
        self._empty_store()
        self._lock = threading.RLock()
        self._initialised: bool = False

        self._bind_handlers()

    def _empty_store(self):
        self._users_by_id: Dict[str, User] = {}

    def _add_user(self, data: dict):
        user = User.from_dict(data)
        self._users_by_id[user.user_id] = user
        return user

    def _initialise(self):
        with self._lock:
            if self._initialised:
                # Fast exit for initialisation while waiting on lock
                return
            self._empty_store()
            for page in self._bot.api.users.list.paginate():
                for user in page['members']:
                    self._add_user(user)

    def reload(self):
        self._initialised = False
        self._initialise()

    def get(self, user_id: str, default: Optional[T] = None,
            use_cache: bool = True) -> Union['User', Optional[T]]:
        if use_cache and not self._initialised:
            self._initialise()
        if user_id in self._users_by_id:
            return self._users_by_id[user_id]
        elif not use_cache:
            resp = self._bot.api.users.info(user=user_id)
            if not resp.get('ok'):
                return default
            with self._lock:
                return self._add_user(resp['user'])
        else:
            return default

    def populate_from_team_state(self, data_dict: dict):
        with self._lock:
            self._initialised = True
            self._empty_store()
            for user in data_dict['users']:
                self._add_user(user)
            self._bot.logger.info(f"Loaded {len(self._users_by_id)} users from team state")

    def _bind_handlers(self) -> None:
        PREFIX = "_on_"
        for name in dir(type(self)):
            if not name.startswith(PREFIX):
                continue
            attr = getattr(self, name)
            mtype = name[len(PREFIX):]
            self._bot.on(mtype, attr)

    def _on_user_change(self, evt):
        user = self._users_by_id[evt['user']['id']]
        if user is not None:
            user.update_from_dict(evt['user'])
        else:
            LOGGER.error("User change event for unknown user - adding")
            with self._lock:
                self._add_user(evt['user'])

    def _on_team_join(self, evt):
        with self._lock:
            self._add_user(evt['user'])


class User(object):
    def __init__(self, user_id: str,
                 deleted: bool,
                 is_admin: bool,
                 is_owner: bool,
                 is_bot: bool,
                 display_name: str,
                 real_name: str,
                 lock: Optional[threading.RLock] = None) -> None:
        self.user_id = user_id
        self.deleted = deleted
        self.is_admin = is_admin
        self.is_owner = is_owner
        self.is_bot = is_bot
        self.display_name = display_name
        self.real_name = real_name
        self.name = display_name or real_name
        if lock is None:
            lock = threading.RLock()
        self._lock = lock

    @classmethod
    def _parse_dict(self, data_dict: dict) -> dict:
        return {"user_id": data_dict['id'],
                "deleted": data_dict.get('deleted', False),
                "is_admin": data_dict.get('is_admin', False),
                "is_owner": data_dict.get('is_owner', False),
                "is_bot": data_dict.get('is_bot', False),
                "display_name": data_dict.get('profile', {}).get('display_name'),
                "real_name": data_dict.get('profile', {}).get('real_name')}

    @classmethod
    def from_dict(cls: Type[UserT], data: dict) -> UserT:
        return cls(**cls._parse_dict(data))

    def update_from_dict(self, data: dict) -> None:
        # Sorry that this is kind of hacky. It dramatically
        # reduces code duplication so I'm not that sorry.
        with self._lock:
            type(self).__init__(self, lock=self._lock, **self._parse_dict(data))
