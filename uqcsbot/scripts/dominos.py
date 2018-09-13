import argparse
from uqcsbot import bot, Command
from bs4 import BeautifulSoup
from datetime import datetime
from requests.exceptions import RequestException
from uqcsbot.utils.command_utils import loading_status, UsageSyntaxException
import requests

MAX_COUPONS = 10 # Prevents abuse
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

    def keyword_matches(self, keyword: str) -> bool:
        return keyword.lower() in self.description.lower()

@bot.on_command("dominos")
@loading_status
def handle_dominos(command: Command):
    '''
    `!dominos [--num] N [--expiry] <KEYWORDS>` - Returns a list of dominos coupons (default: 5 | max: 10)
    '''
    command_args = command.arg.split() if command.has_arg() else []

    parser = argparse.ArgumentParser()

    def usage_error(*args, **kwargs):
        raise UsageSyntaxException()
    parser.error = usage_error # type: ignore
    parser.add_argument('-n', '--num', default=5, type=int)
    parser.add_argument('-e', '--expiry', action='store_true')
    parser.add_argument('keywords', nargs='*')

    args = parser.parse_args(command_args)
    coupons_amount = min(args.num, MAX_COUPONS)
    coupons = get_coupons(coupons_amount, args.expiry, args.keywords)

    message = ""
    for coupon in coupons:
        message += f"Code: *{coupon.code}* - {coupon.description}\n"
    bot.post_message(command.channel_id, message)

def filter_coupons(coupons: list, keywords: list) -> list:
    '''
    Filters coupons iff a keyword is found in the description.
    '''
    return [coupon for coupon in coupons if \
            any(coupon.keyword_matches(keyword) for keyword in keywords)]
        
def get_coupons(n: int, ignore_expiry: bool, keywords: list) -> list:
    '''
    Returns a list of n Coupons
    '''

    coupon_page = get_coupon_page()
    if coupon_page is None:
        return None
    
    coupons = get_coupons_from_page(coupon_page)

    if not ignore_expiry:
        coupons = [coupon for coupon in coupons if coupon.is_valid()]

    if keywords:
        coupons = filter_coupons(coupons, keywords)
    return coupons[:n]

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
