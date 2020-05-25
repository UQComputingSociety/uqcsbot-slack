from uqcsbot import bot
from uqcsbot.utils.command_utils import HYPE_REACTS
from bs4 import BeautifulSoup
from datetime import datetime
from random import choice
from requests.exceptions import RequestException
import requests
import csv

HOLIDAY_URL = "https://www.timeanddate.com/holidays/fun/"
HOLIDAY_CSV_PATH = "uqcsbot/static/geek_holidays.csv"


class Holiday:
    def __init__(self, date: datetime, description: str, url: str) -> None:
        self.date = date
        self.description = description
        self.url = url

    def is_today(self) -> bool:
        """
        Returns true if the holiday is celebrated today
        """
        now = datetime.now()
        return self.date.month == now.month and self.date.day == now.day


@bot.on_schedule('cron', hour=9, timezone='Australia/Brisbane')
def holiday() -> None:
    """
    Posts a random celebratory day on #general from
    https://www.timeanddate.com/holidays/fun/
    """
    channel = bot.channels.get("general")

    holiday = get_holiday()
    if holiday is None:
        return

    message = bot.post_message(channel, f'Today is {holiday.description}!')
    bot.api.reactions.add(name=choice(HYPE_REACTS), channel=channel.id, timestamp=message['ts'])


def get_holiday() -> Holiday:
    """
    Gets the holiday for a given day. If there are multiple
    holidays, choose a random one.
    """
    holiday_page = get_holiday_page()
    if holiday_page is None:
        return None

    geek_holidays = get_holidays_from_csv()
    holidays = get_holidays_from_page(holiday_page)

    holidays_today = [holiday for holiday in holidays + geek_holidays if holiday.is_today()]

    return choice(holidays_today) if holidays_today else None


def get_holidays_from_page(holiday_page) -> list:
    """
    Strips results from html page
    """
    soup = BeautifulSoup(holiday_page, 'html.parser')
    soup_holidays = (soup.find_all(class_="c0") + soup.find_all(class_="c1")
                     + soup.find_all(class_="hl"))

    holidays = []

    for soup_holiday in soup_holidays:
        date_string = soup_holiday.find('th').get_text(strip=True)
        description = soup_holiday.find('a').get_text(strip=True)
        url = soup_holiday.find('a')['href']
        date = datetime.strptime(date_string, '%d %b')
        holiday = Holiday(date, description, url)
        holidays.append(holiday)

    return holidays


def get_holidays_from_csv():
    """
    Returns list of holiday objects, one for each holiday in csv file
    csv rows in format: date,description,link
    """
    holidays = []
    with open(HOLIDAY_CSV_PATH, "r") as csvfile:
        for row in csv.reader(csvfile):
            date = datetime.strptime(row[0], "%d %b")
            holiday = Holiday(date, row[1], row[2])
            holidays.append(holiday)

    return holidays
                

def get_holiday_page() -> bytes:
    """
    Gets the holiday page HTML
    """
    try:
        response = requests.get(HOLIDAY_URL)
        return response.content
    except RequestException as e:
        bot.logger.error(e.response.content)
    return None
