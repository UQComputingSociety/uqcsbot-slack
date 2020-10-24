"""
Monitors #jobs-bulletin and reminds employers and users of their rights and responsibilities.
"""
from uqcsbot import bot
from uqcsbot.utils.message_utils import insert_channel_links
import time

MESSAGE_PAUSE = 2   # Number of seconds between sending bot messages
JOBS_BOARD = "https://link.uqcs.org/jobs"
FAIR_WORK_INFO = "https://www.fairwork.gov.au/pay/unpaid-work/work-experience-and-internships"
EAIT_UNPAID_JOBS = "https://www.eait.uq.edu.au/engineering-professional-practice-unpaid-placements"
EAIT_FACULTY = "https://www.eait.uq.edu.au/"
CODE_OF_CONDUCT = "https://github.com/UQComputingSociety/code-of-conduct"
UQCS_EMAIL = "mailto:contact@uqcs.org.au"
WELCOME_MESSAGES = [    # Welcome messages sent to new members
    "#jobs-bulletin is a little different to your average"
    + " UQCS :slack: channel and has a few extra rules:",
    "*Rules for Everyone* \n"
    "1. The _only_ posts allowed in this channel are job advertisements.\n"
    "2. All discussion about the posted jobs must take place in the #jobs-discussion "
    + " channel or by direct message with the person posting the advertisement."
    + " Please be respectful when interacting with companies and sponsors.",
    "*Additional Rules for Employers Posting Jobs/Internship Opportunities:*\n"
    "3. We take the rights of our members and associates seriously. If you are posting an unpaid"
    + " position, please be up front about the lack of remuneration and *mindful of*"
    + f" <{FAIR_WORK_INFO}|*your obligations*> under the"
    + " _Fair Work Act (2009)_ :fairwork:. \n"
    "_> tldr: if an intern (whether called that or not) adds value to"
    + " (or 'does productive work' for) your business, they must be remunerated with a fair wage._"
    + " If you ignore these warnings, please expect to face criticism from the community"
    + " (we will protect our members from being exploited)."
    + f" Additionally, all <{EAIT_UNPAID_JOBS}|unpaid placements> for students in the"
    + f" <{EAIT_FACULTY}|EAIT Faculty> must be approved by the faculty placement advisers.",
    f"4. Job postings _must_ conform to our <{CODE_OF_CONDUCT}|Code of Conduct>"
    + " and must not discriminate against applicants based on race, religion,"
    + " sexual orientation, gender identity or age.",
    "If you have any questions, please get in touch with the committee in"
    + f" #uqcs-meta or by email at <{UQCS_EMAIL}|contact@uqcs.org.au>."
]


@bot.on("member_joined_channel")
def welcome_jobs(event: dict):
    """
    Welcomes job seekers and employers to the #jobs-bulletin
    channel, setting expectations for both.

    @no_help
    """
    chan = bot.channels.get(event.get("channel"))
    if chan is None or chan.name != "jobs-bulletin":
        return

    user = bot.users.get(event.get("user"))

    if user is None or user.is_bot:
        return

    # Send instructions to user
    bot.post_message(user.user_id,
                     insert_channel_links(f"Hey {user.name}, welcome to #jobs-bulletin!"))
    for message in WELCOME_MESSAGES:
        time.sleep(MESSAGE_PAUSE)
        bot.post_message(user.user_id, insert_channel_links(message))


@bot.on("message")
def job_response(evt: dict):
    """
    Messages users that have posted in #jobs-bulletin to remind them of the rules.

    @no_help
    """
    channel = bot.channels.get(evt.get("channel"))

    if not channel:
        return

    if channel.name != "jobs-bulletin":
        return

    if evt.get("subtype") in ["channel_join", "channel_leave"]:
        return

    jobs_bulletin = channel

    user = bot.users.get(evt.get("user"))

    if user is None or user.is_bot:
        return

    channel_message = (f"{user.name} has posted a new job in #jobs-bulletin! :tada: \n"
                       f"Please ask any questions in #jobs-discussion"
                       + f" or in a private message to <@{user.user_id}>")
    bot.post_message(jobs_bulletin, insert_channel_links(channel_message))

    user_message = (f"Hey {user.name}, you've just posted in #jobs-bulletin! \n"
                    f"Just a quick reminder of the conditions"
                    + f" surrounding the use of this channel:\n" +
                    f"\n".join(WELCOME_MESSAGES[1:] + [""]) +
                    f"*Broken one of these rules?*\n"
                    f"It's not too late! Please go back ASAP and"
                    + f" edit your message in #jobs-bulletin so it complies (or ask a committee"
                    + f" member to delete it). Thanks!")
    bot.post_message(user.user_id, insert_channel_links(user_message))


@bot.on_schedule("cron", hour=9, day_of_week='mon', timezone='Australia/Brisbane')
def jobs_board():
    """
    Lets people know the UQCS jobs board exists by messaging #jobs-discussion every week.
    """
    channel = bot.channels.get("jobs-discussion")
    message = f"Looking for an internship, a grad job, or something casual? \n Why not check out " \
              f"our job board at <{JOBS_BOARD}|link.uqcs.org>.\n Got a job to offer, or " \
              f"something wrong/out of date? Ping `@committee` and let us know."

    message = bot.post_message(channel, message)
    bot.api.reactions.add(name="briefcase", channel=channel.id, timestamp=message.get("ts"))
