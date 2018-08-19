from uqcsbot import bot
from uqcsbot.utils.command_utils import HYPE_REACTS
from bs4 import BeautifulSoup
from random import choice
import datetime
import requests

HOLIDAY_URL = 'https://www.timeanddate.com/holidays/fun/'

@bot.on_schedule('cron', hour=9, timezone='Australia/Brisbane')
def holiday():
    '''
    Posts a random celebratory day on #general from
    https://www.timeanddate.com/holidays/fun/
    '''
    channel = bot.channels.get("general")

    now = datetime.datetime.now().strftime("%d %b").lstrip('0')
    holiday = get_holiday(now)
    if holiday is None:
        return

    description = holiday['desc']
    message = bot.post_message(channel, f'Today is {description}!')
    bot.api.reactions.add(name=choice(HYPE_REACTS),
                          channel=channel.id,
                          timestamp=message['ts'])

def get_holiday(day:str) -> dict:
    '''
    Gets the holiday for a given day. If there are multiple
    holidays, choose a random one.
    '''
    holiday_page = get_holiday_page()
    if holiday_page is None:
        return None

    holidays = get_holidays_from_page(holiday_page)

    holidays_today = [holiday for holiday in holidays if day in holiday['day']]

    return choice(holidays_today) if holidays_today else None

    
def get_holidays_from_page(holiday_page) -> list:
    '''
    Strips results from html page
    '''
    soup = BeautifulSoup(holiday_page, 'html.parser')
    soup_holidays = soup.find_all(class_="c0") + \
                    soup.find_all(class_="c1") + \
                    soup.find_all(class_="hl")

    holidays = []

    for soup_holiday in soup_holidays:
        holiday = {}
        holiday['day'] = soup_holiday.find('th').get_text(strip=True)
        holiday['desc'] = soup_holiday.find('a').get_text(strip=True)
        holiday['url'] = soup_holiday.find('a')['href']
        holidays.append(holiday)

    return holidays

def get_holiday_page() -> bytes:
    '''
    Gets the holiday page HTML
    '''
    try:
        response = requests.get(HOLIDAY_URL)
        return response.content
    except RequestException as e:
        bot.logger.error(e.content)
    return None
