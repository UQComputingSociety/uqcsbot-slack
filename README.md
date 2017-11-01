# uqcsbot

uqcsbot is a chat bot built on the [Hubot][hubot] framework for use on our [UQCS Slack Team](uqcs.slack.com).

#### Set-up in Windows (with cygwin)

0. Ensure node, npm and cygwin are installed
1. `npm install`
2. `dos2unix bin/hubot`
3. `bin/hubot`

### Running uqcsbot locally

**If you're having trouble building/running the bot, don't be afraid to ask for help in the UQCS slack**

You can test your hubot by running the following, however some plugins will not
behave as expected unless the [environment variables](#configuration) they rely
upon have been set.

You can start uqcsbot locally by running:

    % bin/hubot

You'll see some start up output and a prompt:

    [Sat Feb 28 2015 12:38:27 GMT+0000 (GMT)] INFO Using default redis on localhost:6379
    uqcsbot>

Then you can interact with uqcsbot by typing `uqcsbot help`.

    uqcsbot> uqcsbot help
    uqcsbot animate me <query> - The same thing as `image me`, except adds [snip]
    uqcsbot help - Displays all of the help commands that uqcsbot knows about.
    ...

### Running the bot on our test slack

We've created a test slack just for testing bot features out.

How to use:
1. [Join the test slack by clicking here](https://uqcstest-inviter.herokuapp.com/)
2. Pick one of the bots to use (make sure no one else is using them first!)
3. Run your bot like so: `bin/hubot --adapter slack [0-3]` where the number is the number of the bot you want to run.
4. Enjoy testing :)

There's currently 4 public bot tokens avaliable for usage, please check others aren't using them before you use one. If you want to test our more complicated/advanced features it's probably easier to setup your own dummy slack as described below.

Tokens (name: number):
- alpha: 0
- beta: 1
- gamma: 2
- delta: 3

### Running the bot locally on a dummy slack

If you want to test some slack specific features (e.g. emoji's):

0. Ensure you have the bot running in it's command line form as above (ask in slack if you're having trouble)
1. Create a [slack team](https://slack.com/get-started)
2. Now you need to add a new bot go [here](https://slack.com/apps), ensuring you have your newly created team selected
3. Search for "Bots"
4. Add a new configuration
5. Setup a new enviromental variable: `HUBOT_SLACK_TOKEN=xoxb-YOUR-TOKEN-HERE`
6. Run your bot like so: `bin/hubot --adapter slack`
7. Your bot should now connect to your slack, make sure you invite your bot to any channels you want it to work in.

### Scripting

Looking through the existing scripts (/scripts) is a great way to learn how to interact with Hubot and write your first script. Be sure to check out Hubot's own [Scripting Guide](scripting-docs) for more examples.

For any further help or information, the `bot-testing` channel on UQCS slack is the best place to ask any questions!

[scripting-docs]: https://github.com/hubotio/hubot/blob/master/docs/scripting.md
