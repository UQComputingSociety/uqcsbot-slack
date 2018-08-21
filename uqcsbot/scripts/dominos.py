from uqcsbot import bot, Command
from bs4 import BeautifulSoup
from datetime import datetime
from requests.exceptions import RequestException
from uqcsbot.utils.command_utils import loading_status
import requests

COUPONESE_DOMINOS_URL = 'https://www.couponese.com/store/dominos.com.au/'

class Coupon:
    def __init__(self, code: str, expiry_date: str, description: str) -> None:
        self.code = code
        self.expiry_date = expiry_date
        self.description = description
    
    def is_valid(self) -> bool:
        try:
            expiry_date = datetime.strptime(self.expiry_date, '%Y-%m-%d')
            now = datetime.now()
            return expiry_date.year >= now.year and expiry_date.month >= now.month and\
                expiry_date.day >= now.day
        except:
            return True

@bot.on_command("dominos")
@loading_status
def handle_dominos(command: Command):
    '''
    `!dominos <n>` - Returns n domino's coupons
    '''
    command_args = command.arg.strip() if command.has_arg() else 5

    coupons = get_coupons(int(command_args))
    message = ""
    for coupon in coupons:
        message += f"Code: *{coupon.code}* - {coupon.description}\n"
    bot.post_message(command.channel_id, message)

def get_coupons(n:int) -> list:
    coupon_page = get_coupon_page()
    if coupon_page is None:
        return None
    
    coupons = get_coupons_from_page(coupon_page)

    valid_coupons = [coupon for coupon in coupons if coupon.is_valid()]
    return valid_coupons[:n]

def get_coupons_from_page(coupon_page: bytes) -> list:
    '''
    Strips results from html page and returns a list of Coupon(s)
    '''
    soup = BeautifulSoup(coupon_page, 'html.parser')
    soup_coupons = soup.find_all(class_="ov-coupon")

    coupons = []

    for soup_coupon in soup_coupons:
        expiry_date_str = soup_coupon.find(class_='ov-expiry').get_text(strip=True)
        description = soup_coupon.find(class_='ov-desc').get_text(strip=True)
        code = soup_coupon.find(class_='ov-code').get_text(strip=True)
        coupon = Coupon(code, expiry_date_str, description)
        coupons.append(coupon)

    return coupons

def get_coupon_page() -> bytes:
    '''
    Gets the coupon page HTML
    '''
    try:
        response = requests.get(COUPONESE_DOMINOS_URL)
        return response.content
    except RequestException as e:
        bot.logger.error(e.response.content)
    return None
