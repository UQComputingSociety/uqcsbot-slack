from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
from . import api, command_handler
import os

SLACK_VERIFICATION_TOKEN = os.environ.get("SLACK_VERIFICATION_TOKEN", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")

slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/uqcsbot/events")
slack_client = SlackClient(SLACK_BOT_TOKEN)

command_handler = command_handler.CommandHandler(slack_events_adapter, slack_client)
bot = api.Bot(slack_client)
