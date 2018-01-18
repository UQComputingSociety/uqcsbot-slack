# uqcsbot

uqcsbot is a chat bot built in python for use on our [UQCS Slack Team](uqcs.slack.com).

## How to run

1. Optionally set up a virtualenv. I recommend this because of the FLASK_APP environment variable.
1. `python setup.py install`
1. Set an evironment variable for `FLASK_APP` to `uqcsbot/uqcsbot.py`
1. Run the app with `flask run`
