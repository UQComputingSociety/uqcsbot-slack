"""
Welcomes new users to UQCS Slack and check for member milestones
"""
from uqcsbot import bot
import asyncio

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
async def welcome(evt: dict):
    """
    Welcomes new users to UQCS Slack and checks for member milestones

    @no_help
    """
    chan = bot.channels.get(evt.get('channel'))
    if chan is None or chan.name != "announcements":
        return

    announcements = chan
    general = bot.channels.get("general")

    user_info = await bot.run_async(bot.api.users.info, user=evt.get("user"))
    display_name = user_info.get("user", {}).get("profile", {}).get("display_name")

    if display_name:
        await bot.run_async(bot.post_message, general, f"Welcome, {display_name}")

    for message in WELCOME_MESSAGES:
        await asyncio.sleep(MESSAGE_PAUSE)
        await bot.run_async(bot.post_message, evt.get("user"), message)
    if len(announcements.members) % MEMBER_MILESTONE == 0:
        await bot.run_async(
            bot.post_message,
            general,
            f":tada: {len(announcements.members)} members! :tada:"
        )
