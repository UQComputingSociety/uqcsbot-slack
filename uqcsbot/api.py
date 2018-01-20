from slackclient import SlackClient


class Bot(object):
    def __init__(self, client: SlackClient):
        self.client = client

    def post_message(self, channel: str, text: str):
        self.client.api_call("chat.postMessage", channel=channel, text=text)