from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import os

SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/uqcsbot/events")
slack_client = SlackClient(SLACK_BOT_TOKEN)

@slack_events_adapter.on("message")
def echo(event_data):
    message = event_data["event"]
    if message.get("subtype") == "bot_message" or not message.get("text").startswith("!echo"):
        return
    message_text = message["text"][5:]
    slack_client.api_call("chat.postMessage", channel=message["channel"], text=message_text)

slack_events_adapter.start(port=5000)