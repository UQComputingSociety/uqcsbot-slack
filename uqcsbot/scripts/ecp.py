from uqcsbot import bot, Command
import requests
from requests.utils import quote
from bs4 import BeautifulSoup

COURSE_URL = 'https://my.uq.edu.au/programs-courses/course.html?course_code='


@bot.on_command('ecp')
async def handle_ecp(command: Command):
    '''
    `!ecp [COURSE CODE]` - Returns the link to the latest ECP for the given
    course code. If unspecified, will attempt to find the ECP for the channel
    the command was called from.
    '''
    channel = command.channel
    course_name = channel.name if not command.has_arg() else command.arg
    http_response = await bot.run_async(requests.get, f"{COURSE_URL}{quote(course_name)}")
    html = BeautifulSoup(http_response.content, 'html.parser')
    if html.find(id="course-notfound"):
        await bot.as_async.post_message(channel, f"Not a valid course code.")
        return
    ecp_link = html.find_all("a", class_="profile-available")
    if not ecp_link:
        await bot.as_async.post_message(channel, f"No available course profiles.")
    else:
        await bot.as_async.post_message(channel, ecp_link[0]['href'])
