from uqcsbot import bot
import requests
import re
from datetime import datetime
from typing import Tuple, List
from dateutil import parser
from bs4 import BeautifulSoup
from pytz import timezone

# Utilities for parsing seminar information from the School of ITEE's seminar listing page at
# https://www.itee.uq.edu.au/seminar-list.
ITEE_BASE_URL = 'https://www.itee.uq.edu.au'
ITEE_SEMINAR_LIST_URL = 'https://www.itee.uq.edu.au/seminar-list'
BRISBANE_TZ = timezone('Australia/Brisbane')
SEMINAR_DETAILS_REGEX = re.compile('group_seminar_details_element')


class InvalidFormatException(Exception):
    """
    Raised when an element in a document could not be parsed correctly
    """
    def __init__(self, url: str, description: str):
        self.message = f'{description} on \'{url}\'.'
        self.url = url
        super().__init__(self.message, self.url)


class HttpException(Exception):
    """
    Raised when a HTTP request returns an unsuccessful (i.e. not 200 OK) status
    code.
    """
    def __init__(self, url: str, status_code: int):
        self.message = f'Received status code {status_code} from \'{url}\'.'
        self.url = url
        self.status_code = status_code
        super().__init__(self.message, self.url, self.status_code)


def get_seminars() -> List[Tuple[str, str, datetime, str]]:
    """
    Returns summary information for upcoming ITEE seminars, comprising
    seminar date, seminar title, venue, and an information link.
    """
    html = BeautifulSoup(get_seminar_summary_page(), 'html.parser')
    summary_table = html.find('table', summary='ITEE Seminar List')
    if (summary_table is None) or (summary_table.tbody is None):
        # When no seminars are scheduled, no table is shown.
        return []

    seminar_rows = summary_table.tbody.find_all('tr')
    seminar_summaries = map(get_seminar_summary, seminar_rows)
    return list(seminar_summaries)


def get_seminar_summary_page() -> bytes:
    """
    Returns the content of the page summarising upcoming seminars.
    This method is stubbed in unit tests.
    :return: The HTML of the page containing upcoming seminar information.
    """
    http_response = requests.get(ITEE_SEMINAR_LIST_URL)
    if http_response.status_code != requests.codes.ok:
        raise HttpException(ITEE_SEMINAR_LIST_URL, http_response.status_code)
    return http_response.content


def get_seminar_summary(seminar_row) -> Tuple[str, str, datetime, str]:
    """
    Returns the seminar summary information for the given seminar
    table row.
    This method makes assumptions about the format of seminar information on the
    UQ website and is likely to break if the website is updated.
    :param seminar_row: The table row element (tr) to parse
    :return: A structure containing seminar information
             in the order: seminar title, link, date, venue.
    """
    elements = seminar_row.find_all('td')
    if len(elements) != 3:
        raise InvalidFormatException(ITEE_SEMINAR_LIST_URL,
                                     f'Unexpected number of elements on seminar row'
                                     f'(found {len(elements)}, expected 3)')

    # The seminar date is in the first column
    seminar_date = parse_seminar_date(elements[0].get_text().strip(), ITEE_SEMINAR_LIST_URL)

    # (Linked) Title information is in the second column
    title = elements[1].get_text().strip()
    link_element = elements[1].a
    if (link_element is None) or (link_element['href'] is None):
        raise InvalidFormatException(ITEE_SEMINAR_LIST_URL,
                                     f'The link for seminar \'{title}\' could not be found')
    link = ITEE_BASE_URL + link_element['href']

    # Venue is in the third column
    venue = elements[2].get_text().strip()

    # Follow the link to obtain the seminar author
    try:
        # Append author name if it could be successfully obtained, otherwise
        # forget about it
        title = title + ' - ' + get_seminar_details(link)
    except (HttpException, InvalidFormatException) as e:
        bot.logger.error(e.message)

    return title, link, seminar_date, venue


def get_seminar_details(seminar_url: str) -> str:
    """
    Obtains the name of the speaker delivering the seminar at the given seminar details URL
    :param seminar_url: the URL containing Seminar details
    :return: the name of the speaker
    """
    html = BeautifulSoup(get_seminar_details_page(seminar_url), 'html.parser')
    seminar_details_element = html.find('div', class_=SEMINAR_DETAILS_REGEX)
    if (seminar_details_element is None) or (seminar_details_element.contents[1] is None):
        raise InvalidFormatException(seminar_url, f'The details for the seminar could not be found')

    return seminar_details_element.contents[1]


def get_seminar_details_page(seminar_url: str) -> bytes:
    """
    Returns the content of the given seminar details page.
    This method is stubbed in unit tests.
    :return: The HTML of the page containing seminar details.
    """
    http_response = requests.get(seminar_url)
    if http_response.status_code != requests.codes.ok:
        raise HttpException(seminar_url, http_response.status_code)
    return http_response.content


def parse_seminar_date(date_string: str, url: str) -> datetime:
    """
    Parses a date string as Brisbane Time.
    """
    parser_info = parser.parserinfo(dayfirst=True)
    try:
        # The dates and times on the seminars page don't specify a timezone, so
        # the datetime returned by the parser will always be a native datetime
        date = parser.parse(date_string, parser_info)
        # Therefore, we must set the Brisbane Time Zone information.
        return date.replace(tzinfo=BRISBANE_TZ)
    except Exception:
        raise InvalidFormatException(url, f'Could not parse the date {date_string}')
