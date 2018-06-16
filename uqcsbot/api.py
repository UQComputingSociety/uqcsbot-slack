from functools import partial
import time
from slackclient import SlackClient
import asyncio
import threading
from typing import TYPE_CHECKING, List, Iterable, Optional, Generator, Any, Union, TypeVar, Dict
if TYPE_CHECKING:
    from .base import UQCSBot
import logging

T = TypeVar('T')

LOGGER = logging.getLogger(__name__)


class Paginator(Iterable[dict]):
    """
    Provides synchronous and asynchronous iterators over the pages of responses
    from a cursor-based paginated Slack

    See https://api.slack.com/docs/pagination for details
    """
    def __init__(self, client, method, **kwargs):
        self._client = client
        self._method = method
        self._kwargs = kwargs

    def _gen(self) -> Generator[dict, Any, None]:
        kwargs = self._kwargs.copy()
        while True:
            page = self._client.api_call(self._method, **kwargs)
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
    def __init__(self, client: SlackClient, method: str) -> None:
        self._client = client
        self._method = method

    def __call__(self, **kwargs) -> dict:
        """
        Perform the relevant API request. Equivalent to SlackClient.api_call
        except the `method` argument is filled in.

        Attempts to retry the API call if rate-limited.
        """
        fn = partial(
            self._client.api_call,
            self._method,
            **kwargs
        )
        retry_count = 0
        while retry_count < 5:
            result = fn()
            if not result['ok'] and result['error'] == 'ratelimited':
                retry_after_secs = int(result['headers']['Retry-After'])
                LOGGER.info(f'Rate limited, retrying in {retry_after_secs} seconds')
                time.sleep(retry_after_secs)
                retry_count += 1
            else:
                break
        else:
            result = {'ok': False, 'error': 'Reached max rate-limiting retries'}
        if not result['ok']:
            LOGGER.error(f'Slack API error calling {self._method} with kwargs' \
                         + f' {kwargs}: ' + result['error'])
        return result

    def paginate(self, **kwargs) -> Paginator:
        """
        Returns a `Paginator` which allows you to iterate over each page of
        response data from a Slack response that is paginated in the
        cursor-style.

        Count/oldest/latest and page/count methods require manual pagination.
        """
        return Paginator(self._client, self._method, **kwargs)

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
            client=self._client,
            method=f'{self._method}.{item}',
        )


class APIWrapper(object):
    """
    Wraps the Slack API client to make it possible to use dotted methods. Can
    perform API requests both synchronously and asynchronously.

    Example usage:
        > api = APIWrapper(client)
        > api.chat.postMessage(channel="general", text="message")
    """
    def __init__(self, client: SlackClient) -> None:
        self._client = client

    def __getattr__(self, item) -> APIMethodProxy:
        return APIMethodProxy(
            client=self._client,
            method=item,
        )

    def __repr__(self) -> str:
        return f"<APIWrapper of {repr(self._client)}>"


class Channel(object):
    def __init__(
            self,
            bot: 'UQCSBot',
            channel_id: str,
            name: str,
            is_group: bool = False,
            is_im: bool = False,
            is_public: bool = False,
            is_private: bool = False,
            is_archived: bool = False,
            previous_names: List[str] = None
    ) -> None:
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
        return self._member_ids

class ChannelWrapper(object):
    def __init__(self, bot: 'UQCSBot') -> None:
        self._bot = bot
        self._initialised = False
        self._channels_by_id = {}  # type: Dict[str, dict]
        self._channels_by_name = {}  # type: Dict[str, dict]
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
        chan = Channel(
            bot=self._bot,
            channel_id=chan_dict['id'],
            name=chan_dict['name'],
            is_group=chan_dict.get('is_group', False),
            is_im=chan_dict.get('is_im', False),
            is_public=chan_dict.get('is_public', False),
            is_private=chan_dict.get('is_private', False),
            is_archived=chan_dict.get('is_archived', False),
        )
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
            for page in self._bot.api.channels.list.paginate():
                for chan in page['channels']:
                    self._add_channel(chan)
            for group in self._bot.api.groups.list(exclude_members=True).get('groups', []):
                self._add_channel(group)
            # The ims cover the direct messages between the bot and users
            for page in self._bot.api.im.list.paginate():
                for im in page['ims']:
                    if im['is_user_deleted']:
                        continue
                    # Set the channel name to the user being directly messaged
                    # for easier reverse lookups. Note: `user` here is the
                    # user_id.
                    im['name'] = im['user']
                    self._add_channel(im)
            self._initialised = True

    def reload(self):
        self._initialised = False
        self._initialise()

    def get(self, name_or_id: str, default: T = None, use_cache: bool =True) -> Union[Channel, T]:
        if use_cache and not self._initialised:
            self._initialise()
        if name_or_id in self._channels_by_id:
            return self._channels_by_id[name_or_id]
        elif name_or_id in self._channels_by_name:
            return self._channels_by_name[name_or_id]
        elif not use_cache:
            with self._lock:
                resp = self._bot.api.channels.info(channel=name_or_id)
                if not resp.get('ok'):
                    return default
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
        members = chan.members
        with chan._lock:
            members.append(evt['user'])

    def _on_member_left_channel(self, evt):
        chan = self.get(evt['channel'])
        members = chan.members
        with chan._lock:
            members.remove(evt['user'])

    def _on_channel_rename(self, evt):
        with self._lock:
            chan = self.get(evt['channel']['id'])
            self._channels_by_name.pop(chan.name)
            new_channel_name = evt['channel']['name']
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

class MembersWrapper(object):
    pass
