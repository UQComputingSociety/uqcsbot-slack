"""
Welcomes new users to UQCS Slack and check for member milestones
"""
from uqcsbot import bot
import time

MEMBER_MILESTONE = 50  # Number of members between posting a celebration
MESSAGE_PAUSE = 2.5   # Number of seconds between sending bot messages
WELCOME_MESSAGES = [    # Welcome messages sent to new members
    "Hey there! Welcome to the UQCS Slack!",
    "This is the first time I've seen you, so you're probably new here",
    "I'm UQCSbot, your friendly (open source) robot helper",
    "We've got a bunch of generic channels (e.g. #banter, #games, #projects) along with many"
    + " subject-specific ones (e.g #csse1001, #math1051, #csse2310)",
    "To find and join a channel, tap on the channels header in the sidebar",
    "The UQCS Slack is a friendly community with a code of conduct in place to ensure our"
    + " members well-being and safety. You can view a copy of this code of conduct at:"
    + "\n>https://github.com/UQComputingSociety/code-of-conduct",
    "Your friendly committee and admins are:"
    + "\n>Madhav Kumar (@kumar-ish)\n>Matthew Low (@mcl)\n>Bradley (@Σ)"
    + "\n>Sanni Bosamia (@sanni)\n>Jack Caperon (@jam)\n>James Copperthwaite (@jcopperthwaite)"
    + "\n>Kenton Lam (@Kenton)\n>Nicholas Lambourne (@noodle)\n>Olivia Mackenzie-Ross (@Liv)"
    + "\n>Raghav Mishra (@rm)\n>Brian Riwu Kaho (@pipInstall)",
    "For a list of upcoming events check out the #events channel, or type \"!events\"",
    "Type \"help\" here, or \"!help\" anywhere else to find out what I can do!",
    "Be sure to download the Slack desktop and phone apps as well,"
    + " so you'll be able to catch any important announcements",
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
        if any([member is None, member.deleted, member.is_bot]):
            continue
        num_members += 1

    # Alert general of any member milestone.
    if num_members % MEMBER_MILESTONE == 0:
        bot.post_message(general, f":tada: {num_members} members! :tada:")

    # Send new user their welcome messages.
    for message in WELCOME_MESSAGES:
        time.sleep(MESSAGE_PAUSE)
        bot.post_message(user.user_id, message)
