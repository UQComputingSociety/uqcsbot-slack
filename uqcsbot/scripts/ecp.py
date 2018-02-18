from uqcsbot import bot, Command
from requests import get
from requests.utils import quote
from bs4 import BeautifulSoup

COURSE_URL = 'https://my.uq.edu.au/programs-courses/course.html?course_code='


@bot.on_command('ecp')
async def handle_ecp(command: Command):
    channel = command.channel
    course_name = channel.name if not command.has_arg() else command.arg
    http_response = await bot.run_async(get, f"{COURSE_URL}{quote(course_name)}")
    html = BeautifulSoup(http_response.content, 'html.parser')
    if html.find(id="course-notfound"):
        bot.post_message(channel, f"Not a valid course code.")
        return
    ecp_link = html.find_all("a", class_="profile-available")
    if not ecp_link:
        bot.post_message(channel, f"No available course profiles.")
    else:
        bot.post_message(channel, ecp_link[0]['href'])
