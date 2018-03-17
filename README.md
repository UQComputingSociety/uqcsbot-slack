# uqcsbot

uqcsbot is a chat bot built in python for use on our [UQCS Slack Team](uqcs.slack.com).

## Setting up the bot

Run `pip install -e .`

## Running the bot in a local development environment

Run `python3 -m uqcsbot --local`

**Note**: If you're wanting to test/interact with Slack-specific features (e.g. reactions, channels), you _must_ be running the bot with Slack (See following sections).

## Running the bot in the communal dev Slack team

1. Ensure you've joined the [uqcstesting Slack team](https://uqcstest-inviter.herokuapp.com/)
2. Run `python3 -m uqcsbot --dev`

If a bot was available, it will now be running on uqcstesting.

## Running the bot in a custom Slack team

1. [Create a Slack workspace](https://slack.com/create)
2. Run `pip install -e .`
3. [Create a new Slack app](https://api.slack.com/apps/)
4. Add a bot user to your app
5. Install your app to your workspace. Install App > Install App to Workspace
6. Copy the Bot User OAuth Access Token and set it as an environment variable under `SLACK_BOT_TOKEN`
7. Go to Basic Information, copy your Verification Token and set it as an environment variable under `SLACK_VERIFICATION_TOKEN`
8. Run `python3 -m uqcsbot`

The bot will now be running on your custom Slack.

## Tests

Run `pip install -e .[test]` to install the additional packages for testing.

The bot uses [pytest](https://docs.pytest.org/en/latest/). You can run the tests with the command `pytest` from the project's root directory. It should automatically discover the tests (which are located in the `tests` directory).

You don't need to have set up a Slack team to run the tests; they capture the messages which would have been sent to Slack by the bot.

All new scripts must come with tests before they will be accepted into the bot.
