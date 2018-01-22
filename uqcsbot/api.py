from typing import List
from slackclient import SlackClient


# see https://api.slack.com/docs/pagination for details
def paginate_api_call(client: SlackClient, method: str, *args, **kwargs) -> List[dict]:
    pages = []
    while kwargs.get("cursor") != "":
        page = client.api_call(method, *args, **kwargs)
        pages.append(page)
        kwargs["cursor"] = page["response_metadata"]["next_cursor"]
    return pages


class Channel(object):
    def __init__(self, client: SlackClient, channel_id: str):
        self.client = client
        self.id = channel_id

    def get_members(self) -> List[str]:
        member_pages = paginate_api_call(self.client, "conversations.members", channel=self.id)
        members = []
        for page in member_pages:
            members += page["members"]
        return members


class Bot(object):
    def __init__(self, client: SlackClient):
        self.client = client

    def post_message(self, channel: Channel, text: str):
        self.client.api_call("chat.postMessage", channel=channel.id, text=text)
