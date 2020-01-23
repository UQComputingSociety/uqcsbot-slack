"""
Welcomes new users to UQCS Slack and check for member milestones
"""
from uqcsbot import bot
import time

MEMBER_MILESTONE = 50  # Number of members between posting a celebration
MESSAGE_PAUSE = 2.5   # Number of seconds between sending bot messages
LONG_PAUSE = 5   # Number of seconds before follow-up (profile) message is sent
SLACK_DOWNLOAD_GUIDE = "https://slack.com/intl/en-au/help/categories/360000049043-Getting-" \
                       "Started#download-the-slack-app"
UQCSBOT_REPO = "https://github.com/UQComputingSociety/uqcsbot"
SLACK_PROFILE_GUIDE = "https://slack.com/intl/en-au/help/articles/204092246-Edit-your-profile"

WELCOME_MESSAGES = [    # Welcome messages sent to new members
    "Hey there! Welcome to the UQCS Slack!",
    "This is the first time I've seen you, so you're probably new here.",
    f"I'm UQCSbot, your friendly (<{UQCSBOT_REPO}|open source>) robot helper!",
    "We've got a bunch of generic channels (e.g. <#C0D0BEYPM|banter>,"
    + " <#C0DKX7NGP|games>, <#CB2K0Q09K|adulting>) along with many subject-specific"
    + " ones (e.g <#C0MAN4BRS|csse1001>, <#C0Q2KTCK1|math1051>, <#C0DKSDGLE|csse2310>).",
    "To find and join a channel, tap on the channels header in the sidebar.",
    "The UQCS Slack is a friendly community and we have a code of conduct in place to ensure our "
    + "members' well-being and safety. You can view a copy of this code of conduct here:"
    + "\n>https://github.com/UQComputingSociety/code-of-conduct",
    "UQCS elects a leadership committee every year who also serve as our friendly admins. This "
    "year's committee consists of:"
    + "\n>Madhav (<@UFB9R5QFM>)\n>Matthew (<@U8JN3NR1C>)\n>Bradley (<@U4AJ0EDE3>)"
    + "\n>Sanni (<@UM55HGLUT>)\n>Jack (<@U29STGM63>)"
    + "\n>James (<@U1H1R3NGK>)\n>Kenton (<@U9LMBPJG5>)"
    + "\n>Nick (<@U0LG4V4NN>)\n>Olivia (<@UA25BSPGT>)"
    + "\n>Raghav (<@U73H0R0QH>)\n>Brian (<@UCYC0TKMM>)",
    "If you have any questions about UQCS, or need to get in touch, please reach out to them.",
    "For a list of upcoming events check out the <#C0D0G52PP|events> channel and use the command "
    "`!events`.",
    "Type `help` here, or `!help` anywhere else to find out what I can do!",
    f"Be sure to download the Slack <https://slack.com/downloads|desktop> and "
    f"<{SLACK_DOWNLOAD_GUIDE}|mobile> apps as well, so you'll be able to catch any important "
    f"announcements, and again, welcome to the UQ Computing Society :)"
]

PROFILE_MESSAGE = "Don't forget to let people know who you are! Choose a profile pic, set a " \
                  "status and tell us what you're studying. These small touches help the UQCS " \
                  "community understand who you are and, in turn, help you to more quickly " \
                  "become an integral part of the society. If you need any help, check out " \
                  f"this handy <{SLACK_PROFILE_GUIDE}|guide> or ask one admins for help!\n" \
                  f"Once that's all done, why not introduce yourself in <#C2R8W0YPJ|general>."


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
    bot.post_message(general, f"Welcome to UQCS, <@{user.user_id}>! :tada:")

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

    time.sleep(LONG_PAUSE)

    bot.post_message(user.user_id, PROFILE_MESSAGE)
