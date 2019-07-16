from uqcsbot import bot
import requests
from datetime import datetime
from dateutil import parser
from bs4 import BeautifulSoup
from functools import partial
from binascii import hexlify

BASE_COURSE_URL = 'https://my.uq.edu.au/programs-courses/course.html?course_code='
BASE_ASSESSMENT_URL = ('https://www.courses.uq.edu.au/'
                       'student_section_report.php?report=assessment&profileIds=')
BASE_CALENDAR_URL = 'http://www.uq.edu.au/events/calendar_view.php?category_id=16&year='
OFFERING_PARAMETER = 'offer'


class DateSyntaxException(Exception):
    """
    Raised when an unparsable date syntax is encountered.
    """
    def __init__(self, date, course_name):
        self.message = f'Could not parse date \'{date}\' for course \'{course_name}\'.'
        self.date = date
        self.course_name = course_name
        super().__init__(self.message, self.date, self.course_name)


class CourseNotFoundException(Exception):
    """
    Raised when a given course cannot be found for UQ.
    """
    def __init__(self, course_name):
        self.message = f'Could not find course \'{course_name}\'.'
        self.course_name = course_name
        super().__init__(self.message, self.course_name)


class ProfileNotFoundException(Exception):
    """
    Raised when a profile cannot be found for a given course.
    """
    def __init__(self, course_name):
        self.message = f'Could not find profile for course \'{course_name}\'.'
        self.course_name = course_name
        super().__init__(self.message, self.course_name)


class HttpException(Exception):
    """
    Raised when a HTTP request returns an
    unsuccessful (i.e. not 200 OK) status code.
    """
    def __init__(self, url, status_code):
        self.message = f'Received status code {status_code} from \'{url}\'.'
        self.url = url
        self.status_code = status_code
        super().__init__(self.message, self.url, self.status_code)


def get_offering_code(semester=None, campus='STLUC', is_internal=True):
    """
    Returns the hex encoded offering string for the given semester and campus.

    Keyword Arguments:
        semester {str} -- Semester code (3 is summer) (default: current semester)
        campus {str} -- Campus code string (one of STLUC, etc.)
        is_internal {bool} -- True for internal, false for external.
    """
    # TODO: Codes for other campuses.
    if semester is None:
        semester = 1 if datetime.today().month <= 6 else 2
    location = 'IN' if is_internal else 'EX'
    return hexlify(f'{campus}{semester}{location}'.encode('utf-8')).decode('utf-8')


def get_course_profile_url(course_name):
    """
    Returns the URL to the latest course profile for the given course.
    """
    course_url = BASE_COURSE_URL + course_name
    http_response = requests.get(
        course_url, params={OFFERING_PARAMETER: get_offering_code()}
    )
    if http_response.status_code != requests.codes.ok:
        raise HttpException(course_url, http_response.status_code)
    html = BeautifulSoup(http_response.content, 'html.parser')
    if html.find(id='course-notfound'):
        raise CourseNotFoundException(course_name)
    profile = html.find('a', class_='profile-available')
    if profile is None:
        raise ProfileNotFoundException(course_name)
    return profile.get('href')


def get_course_profile_id(course_name):
    """
    Returns the ID to the latest course profile for the given course.
    """
    profile_url = get_course_profile_url(course_name)
    # The profile url looks like this
    # https://course-profiles.uq.edu.au/student_section_loader/section_1/100728
    return profile_url[profile_url.rindex('/')+1:]


def get_current_exam_period():
    """
    Returns the start and end datetimes for the current semester's exam period.

    Note: Assumes that Semester 1 always occurs before or
    during June, with Semester 2 occurring after.
    """
    today = datetime.today()
    current_calendar_url = BASE_CALENDAR_URL + str(today.year)
    http_response = requests.get(current_calendar_url)
    if http_response.status_code != requests.codes.ok:
        raise HttpException(current_calendar_url, http_response.status_code)
    html = BeautifulSoup(http_response.content, 'html.parser')
    event_date_elements = html.findAll('li', class_='description-calendar-view')
    event_date_texts = [element.text for element in event_date_elements]
    current_semester = '1' if today.month <= 6 else '2'
    exam_snippet = f'Semester {current_semester} examination period '
    # The first event encountered is the one which states the commencement of
    # the current semester's exams and also provides the exam period.
    exam_date_text = [t for t in event_date_texts if exam_snippet in t][0]
    start_day, end_date = exam_date_text[len(exam_snippet):].split(' - ')
    end_datetime = parser.parse(end_date)
    start_datetime = end_datetime.replace(day=int(start_day))
    return start_datetime, end_datetime


def get_parsed_assessment_due_date(assessment_item):
    """
    Returns the parsed due date for the given assessment item as a datetime
    object. If the date cannot be parsed, a DateSyntaxException is raised.
    """
    course_name, _, due_date, _ = assessment_item
    if due_date == 'Examination Period':
        return get_current_exam_period()
    parser_info = parser.parserinfo(dayfirst=True)
    try:
        # If a date range is detected, attempt to split into start and end
        # dates. Else, attempt to just parse the whole thing.
        if ' - ' in due_date:
            start_date, end_date = due_date.split(' - ', 1)
            start_datetime = parser.parse(start_date, parser_info)
            end_datetime = parser.parse(end_date, parser_info)
            return start_datetime, end_datetime
        due_datetime = parser.parse(due_date, parser_info)
        return due_datetime, due_datetime
    except Exception:
        raise DateSyntaxException(due_date, course_name)


def is_assessment_after_cutoff(assessment, cutoff):
    """
    Returns whether the assessment occurs after the given cutoff.
    """
    try:
        start_datetime, end_datetime = get_parsed_assessment_due_date(assessment)
    except DateSyntaxException as e:
        bot.logger.error(e.message)
        # If we can't parse a date, we're better off keeping it just in case.
        # TODO(mitch): Keep track of these instances to attempt to accurately
        # parse them in future. Will require manual detection + parsing.
        return True
    return end_datetime >= cutoff if end_datetime else start_datetime >= cutoff


def get_course_assessment(course_names, cutoff=None):
    """
    Returns all the course assessment for the given
    courses that occur after the given cutoff.
    """
    profile_ids = map(get_course_profile_id, course_names)
    joined_assessment_url = BASE_ASSESSMENT_URL + ','.join(profile_ids)
    http_response = requests.get(joined_assessment_url)
    if http_response.status_code != requests.codes.ok:
        raise HttpException(joined_assessment_url, http_response.status_code)
    html = BeautifulSoup(http_response.content, 'html.parser')
    assessment_table = html.find('table', class_='tblborder')
    # Start from 1st index to skip over the row containing column names.
    assessment = assessment_table.findAll('tr')[1:]
    parsed_assessment = map(get_parsed_assessment_item, assessment)
    # If no cutoff is specified, set cutoff to UNIX epoch (i.e. filter nothing).
    cutoff = cutoff or datetime.min
    assessment_filter = partial(is_assessment_after_cutoff, cutoff=cutoff)
    filtered_assessment = filter(assessment_filter, parsed_assessment)
    return list(filtered_assessment)


def get_element_inner_html(dom_element):
    """
    Returns the inner html for the given element.
    """
    return dom_element.decode_contents(formatter='html')


def get_parsed_assessment_item(assessment_item):
    """
    Returns the parsed assessment details for the
    given assessment item table row element.

    Note: Because of the inconsistency of UQ assessment details, I've had to
    make some fairly strict assumptions about the structure of each field.
    This is likely insufficient to handle every course's
    structure, and thus is subject to change.
    """
    course_name, task, due_date, weight = assessment_item.findAll('div')
    # Handles courses of the form 'CSSE1001 - Sem 1 2018 - St Lucia - Internal'.
    # Thus, this bit of code will extract the course.
    course_name = course_name.text.strip().split(' - ')[0]
    # Handles tasks of the form 'Computer Exercise<br/>Assignment 2'.
    task = get_element_inner_html(task).strip().replace('<br/>', ' - ')
    # Handles due dates of the form '26 Mar 18 - 27 Mar 18<br/>Held in Week 6
    # Learning Lab Sessions (Monday/Tuesday)'. Thus, this bit of code will
    # keep only the date portion of the field.
    due_date = get_element_inner_html(due_date).strip().split('<br/>')[0]
    # Handles weights of the form '30%<br/>Alternative to oral presentation'.
    # Thus, this bit of code will keep only the weight portion of the field.
    weight = get_element_inner_html(weight).strip().split('<br/>')[0]
    return (course_name, task, due_date, weight)
