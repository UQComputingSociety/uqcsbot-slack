from typing import Iterable, AsyncIterable, AsyncGenerator, Generator, Any
from functools import partial
from slackclient import SlackClient
import asyncio


class Paginator(Iterable[dict], AsyncIterable[dict]):
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
            page = self._client.api_call(self._method, **self._kwargs)
            yield page
            cursor = page.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break
            kwargs["cursor"] = cursor

    def __iter__(self):
        return self._gen()

    async def _agen(self):
        loop = asyncio.get_event_loop()
        kwargs = self._kwargs.copy()
        request_fn = partial(self._client.api_call, self._method, **kwargs)
        while True:
            page = await loop.run_in_executor(None, request_fn)
            yield page
            cursor = page.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break
            kwargs["cursor"] = cursor

    def __aiter__(self) -> AsyncGenerator[dict, Any]:
        return self._agen()


class APIMethodProxy(object):
    """
    Helper class used to implement APIWrapper
    """
    def __init__(self, client: SlackClient, method: str, is_async: bool = False):
        self._client = client
        self._method = method
        self._async = is_async

    def __call__(self, **kwargs) -> dict:
        """
        Perform the relevant API request. Equivalent to SlackClient.api_call
        except the `method` argument is filled in.

        If the APIMethodProxy was constructed with `is_async=True` runs the
        request asynchronously via:
            asyncio.get_event_loop().run_in_executor(None, req)
        """
        fn = partial(
            self._client.api_call,
            self._method,
            **kwargs
        )
        if self._async:
            loop = asyncio.get_event_loop()
            return loop.run_in_executor(None, fn)
        else:
            return fn()

    def paginate(self, **kwargs) -> Paginator:
        """
        Returns a `Paginator` which can be used as both a synchronous and an
        asynchronous iterable, allowing you to iterate over each page of
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
            is_async=self._async,
        )


class APIWrapper(object):
    """
    Wraps the Slack API client to make it possible to use dotted methods. Can
    perform API requests both synchronously and asynchronously.

    Example usage:
        > api = APIWrapper(client)
        > api.chat.postMessage(channel="general", text="message")

        > async_api = APIWrapper(client, True)
        > await async_api.chat.postMessage(channel="general", text="message")

        > async_api = api(is_async=True)
        > await async_api.chat.postMessage(channel="general", text="message")
    """
    def __init__(self, client: SlackClient, is_async: bool = False):
        self._client = client
        self._async = is_async

    def __getattr__(self, item) -> APIMethodProxy:
        return APIMethodProxy(
            client=self._client,
            method=item,
            is_async=self._async
        )

    def __call__(self, **kwargs) -> 'APIWrapper':
        """
        On call, reconfigure the API Wrapper
        """
        return type(self)(self._client, **kwargs)