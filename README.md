# uqcsbot

uqcsbot is a chat bot built in python for use on our [UQCS Slack Team](uqcs.slack.com).



## Setting up development
Ensure you have Python 3.6 or higher, and `virutalenv` installed.

1. Set up a `virtualenv`. See [virtualenv docs](https://virtualenv.pypa.io/en/stable/) for more information.
1. Activate the `virtualenv`
1. `pip install -r requirements.txt`

### Local environment

To test UQCSbot locally, just use `python -m uqcsbot --dev`. This will create a virtual prompt you can type UQCSBot commands in to.

## Remove environment

The simplest way to test against a remote environment requires you to have [ngrok](https://ngrok.com/) installed.

1. [Create a Slack workspace](https://slack.com/create)
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
