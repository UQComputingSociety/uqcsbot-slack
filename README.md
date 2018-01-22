# uqcsbot

uqcsbot is a chat bot built in python for use on our [UQCS Slack Team](uqcs.slack.com).

## Setting up the local development environment

To run the local development environment, make sure you have Python 3 installed.

1. Run `python setup.py install`
2. Run `python -m uqcsbot --dev`

## Setting up the remote development environment

To set everything up make sure you have Python 3, virtualenv, and [ngrok](https://ngrok.com/)

1. [Create a Slack workspace](https://slack.com/create)
1. Set up a `virtualenv`. See [virtualenv docs](https://virtualenv.pypa.io/en/stable/) for more information.
1. Activate the `virtualenv`
1. `python setup.py install`
1. [Create a new Slack app](https://api.slack.com/apps/)
1. Add a bot user to your app
1. Install your app to your workspace. Install App > Install App to Workspace
1. Copy the Bot User OAuth Access Token and set it as an environment variable under `SLACK_BOT_TOKEN`
1. Go to Basic Information, copy your Verification Token and set it as an environment variable under `SLACK_VERIFICATION_TOKEN`
1. Run `python -m uqcsbot`
1. Run `ngrok http 5000`
1. Copy the https URL (It should look like `https://h7465j.ngrok.io`)
1. Under Event Subscriptions, make sure events are enabled and paste this URL +  `/uqcsbot/events` into the Request URL. (For example `https://h7465j.ngrok.io/uqcsbot/events`)
1. Subscribe to `message.channels` under bot events

The bot should now be receiving all slack events. Because of how ngrok works, you will need to update the `ngrok` URL each time you run it unless you get a paid plan or deploy to an actual server instead of using `ngrok`.