from slackeventsapi import SlackEventAdapter
import os

SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/uqcsbot/events")

@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    print(f'{message["user"]} posted {message["text"]}')

slack_events_adapter.start(port=5000)