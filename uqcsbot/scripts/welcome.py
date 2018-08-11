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
    "We've got a bunch of generic channels (e.g. #banter, #games, #projects) along with many " \
    "subject-specific ones (e.g #csse1001, #math1051, #csse2310)",
    "Your friendly admins are @csa, @rob, @mb, @tomgr, @mitch, @guthers, and @artemis",
    "Type \"help\" here, or \"!help\" anywhere else to find out what I can do!",
    "and again, welcome :)"
]


@bot.on("member_joined_channel")
def welcome(evt: dict):
    """
    Welcomes new users to UQCS Slack and checks for member milestones.

    @no_help
    """
    chan = bot.channels.get(evt.get('channel'))
    if chan is None or chan.name != "announcements":
        return

    announcements = chan
    general = bot.channels.get("general")
    user = bot.users.get(evt.get("user"))

    if user is None or user.is_bot:
        return

    # Welcome user in general.
    bot.post_message(general, f"Welcome, <@{user.user_id}>!")

    # Calculate number of members, ignoring deleted users and bots.
    num_members = 0
    for member_id in announcements.members:
        member = bot.users.get(member_id)
        if member is None or member.deleted or member.is_bot:
            continue
        num_members += 1

    # Alert general of any member milestone.
    if num_members % MEMBER_MILESTONE == 0:
        bot.post_message(general, f":tada: {num_members} members! :tada:")

    # Send new user their welcome messages.
    for message in WELCOME_MESSAGES:
        time.sleep(MESSAGE_PAUSE)
        bot.post_message(user.user_id, message)
