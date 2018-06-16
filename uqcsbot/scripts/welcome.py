"""
Welcomes new users to UQCS Slack and check for member milestones
"""
from uqcsbot import bot
import time

MEMBER_MILESTONE = 50  # Number of members between posting a celebration
MESSAGE_PAUSE = 2.5   # Number of seconds between sending bot messages
WELCOME_MESSAGES = [    # Welcome messages sent to new members
    "Hey there! Welcome to the UQCS slack!",
    "This is the first time I've seen you, so you're probably new here",
    "I'm UQCSbot, your friendly (open source) robot helper",
    "We've got a bunch of generic channels (e.g. #banter, #games, #projects) along with many subject-specific ones",
    "Your friendly admins are @csa, @rob, @mb, @trm, @mitch, @guthers, and @artemis",
    "Type \"help\" here, or \"!help\" anywhere else to find out what I can do!",
    "and again, welcome :)"
]


@bot.on("member_joined_channel")
def welcome(evt: dict):
    """
    Welcomes new users to UQCS Slack and checks for member milestones

    @no_help
    """
    chan = bot.channels.get(evt.get('channel'))
    if chan is None or chan.name != "announcements":
        return

    announcements = chan
    general = bot.channels.get("general")

    user = bot.users.get(evt.get("user"))

    if user:
        bot.post_message(general, f"Welcome, {user.display_name}")

    if user and not user.is_bot:
        for message in WELCOME_MESSAGES:
            time.sleep(MESSAGE_PAUSE)
            bot.post_message(evt.get("user"), message)

    valid_users = len([
        member_id
        for member_id in announcements.members
        # getattr used so `None` members count as "deleted"
        if not getattr(bot.users.get(member_id), "deleted", True)
    ])
    bot.logger.info(f"Currently at {valid_users} members")
    if valid_users % MEMBER_MILESTONE == 0:
        bot.post_message(general, f":tada: {valid_users} members! :tada:")
