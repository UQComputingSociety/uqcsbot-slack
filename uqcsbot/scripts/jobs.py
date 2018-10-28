"""
Monitors #jobs-bulletin and reminds employers and users of their rights and responsibilities.
"""
from uqcsbot import bot
import time

MESSAGE_PAUSE = 2   # Number of seconds between sending bot messages
FAIR_WORK_INTERNSHIPS_INFO = "https://www.fairwork.gov.au/pay/unpaid-work/work-experience-and-internships"
EAIT_UNPAID_JOBS = "https://www.eait.uq.edu.au/engineering-professional-practice-unpaid-placements"
EAIT_FACULTY = "https://www.eait.uq.edu.au/"
CODE_OF_CONDUCT = "https://github.com/UQComputingSociety/code-of-conduct"
UQCS_EMAIL = "mailto:contact@uqcs.org.au"
WELCOME_MESSAGES = [    # Welcome messages sent to new members
    "#jobs-bulletin is a little different to your average UQCS :slack: channel and has a few extra rules:",
    "*Rules for Everyone* \n1. The _only_ posts allowed in this channel are job advertisements.\n"
    "2. All discussion about the posted jobs must take place in the #jobs-discussion channel or by direct message "
    "with the person posting the advertisement. Please be respectful when interacting with companies and sponsors.",
    "*Additional Rules for Employers Posting Jobs/Internship Opportunities:*\n"
    f"3. We take the rights of our members and associates seriously. If you are posting an unpaid position, please be"
    f" up front about the lack of remuneration and *mindful of* <{FAIR_WORK_INTERNSHIPS_INFO}|*your obligations*> "
    "under the _Fair Work Act (2009)_ :fairwork:. \n_tldr: if an intern (whether called that or not) adds value to "
    "(or 'does productive work' for) your business, they must be remunerated with either a fair wage_. If you"
    " ignore these warnings, please expect to face criticism from the community (we will protect our members from being"
    f" exploited). Additionally, all <{EAIT_UNPAID_JOBS}|unpaid placements> for students in the "
    f"<{EAIT_FACULTY}|EAIT Faculty> must be approved by the faculty.",
    f"4. Job postings _must_ conform to our <{CODE_OF_CONDUCT}|Code of Conduct> and must not discriminate against "
    f"applicants based on race, religion, sexual orientation, gender identity or age.",
    f"If you have any questions, please get in touch with the committee in #uqcs-meta or by email at "
    f"<{UQCS_EMAIL}|contact@uqcs.org.au>."
]


@bot.on("member_joined_channel")
def welcome_jobs(evt: dict):
    """
    Welcomes job seekers and employers to the #jobs-bulletin channel, setting expectations for both.

    @no_help
    """
    chan = bot.channels.get(evt.get("channel"))
    if chan is None or chan.name != "jobs-bulletin":
        return

    jobs_bulletin = chan
    user = bot.users.get(evt.get("user"))

    if user is None or user.is_bot:
        return

    # Send instructions to user
    bot.post_message(user.user_id, f"Hey {user.display_name}, welcome to <#{jobs_bulletin.id}>!")
    for message in WELCOME_MESSAGES:
        time.sleep(MESSAGE_PAUSE)
        bot.post_message(user.user_id, message)


@bot.on("message")
def job_response(evt: dict):
    """
    Messages users that have posted in #jobs-bulletin to remind them of the rules.

    @no_help
    """
    chan = bot.channels.get(evt.get("channel"))

    if chan.name != "jobs-bulletin":
        return

    if evt.get("subtype") in ["channel_join", "channel_leave"]:
        return

    jobs_bulletin = chan
    jobs_discussion = bot.channels.get("jobs-discussion")
    user = bot.users.get(evt.get("user"))

    if user is None or user.is_bot:
        return

    bot.post_message(jobs_bulletin, f"{user.display_name} has posted a new job in <#{jobs_bulletin.id}>! "
                                    f":tada: \nPlease ask any questions in <#{jobs_discussion.id}> or in a private "
                                    f"message to <@{user.user_id}|{user.display_name}>")

    bot.post_message(user.user_id, f"Hey {user.display_name}, you've just posted in <#{jobs_bulletin.id}>! "
                                   f"Just a quick reminder of the conditions surrounding the use of this channel:")
    for message in WELCOME_MESSAGES:
        time.sleep(MESSAGE_PAUSE)
        bot.post_message(user.user_id, message)
    bot.post_message(user.user_id, f"*Broken one of these rules?*\n It's not too late! Please go back ASAP and delete"
                                   f" or modify your message in <#{jobs_bulletin.id}> so it complies. Thanks!")
