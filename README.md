# uqcsbot

uqcsbot is a chat bot built in python for use on our [UQCS Slack Team](uqcs.slack.com).

## Setting up the bot

Run `python3 setup.py install`

## Running the bot in a local development environment

Run `python3 -m uqcsbot --local`

**Note**: If you're wanting to test/interact with Slack-specific features (e.g. reactions, channels), you _must_ be running the bot with Slack (See next section).

## Running the bot in the communal dev Slack team

1. Ensure you've joined the [uqcstesting Slack team](https://uqcstest-inviter.herokuapp.com/)
2. Run `python3 -m uqcsbot`

If a bot was available, it will now be running on uqcstesting.