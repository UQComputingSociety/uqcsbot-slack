from uqcsbot import bot
import requests
from datetime import datetime
from dateutil import parser
from bs4 import BeautifulSoup

BASE_COURSE_URL = 'https://my.uq.edu.au/programs-courses/course.html?course_code='
BASE_ASSESSMENT_URL = 'https://www.courses.uq.edu.au/student_section_report.php?report=assessment&profileIds='
BASE_CALENDAR_URL = 'http://www.uq.edu.au/events/calendar_view.php?category_id=16&year='

class DateSyntaxException(Exception):
    '''
    Raised when an unparsable date syntax is encountered.
    '''
    def __init__(self, date):
        super().__init__()
        self.date = date
        bot.logger.error(f'Could not parse date \'{date}\'.')

class CourseNotFoundException(Exception):
    '''
    Raised when a given course cannot be found for UQ.
    '''
    def __init__(self, course_name):
        super().__init__()
        self.course_name = course_name
        bot.logger.error(f'Could not find course \'{course_name}\'.')

class ProfileNotFoundException(Exception):
    '''
    Raised when a profile cannot be found for a given course.
    '''
    def __init__(self, course_name):
        super().__init__()
        self.course_name = course_name
        bot.logger.error(f'Could not find profile for course \'{course_name}\'.')

class HttpException(Exception):
    '''
    Raised when a HTTP request returns an unsuccessful (i.e. not 200) status code.
    '''
    def __init__(self, url, status_code):
        super().__init__()
        self.url = url
        self.status_code = status_code
        bot.logger.error(f'Received status code {status_code} from \'{url}\'.')

async def get_course_profile_url(course_name):
    '''
    Returns the URL to the latest course profile for the given course.
    '''
    course_url = BASE_COURSE_URL + course_name
    http_response = await bot.run_async(requests.get, course_url)
    if http_response.status_code != 200:
        raise HttpException(course_url, http_response.status_code)
    html = BeautifulSoup(http_response.content, 'html.parser')
    if html.find(id='course-notfound'):
        raise CourseNotFoundException(course_name)
    profile = html.find('a', class_='profile-available')
    if profile is None or profile.get('href') is None:
        raise ProfileNotFoundException(course_name)
    return profile.get('href')

async def get_course_profile_id(course_name):
    '''
    Returns the ID to the latest course profile for the given course.
    '''
    profile_url = await get_course_profile_url(course_name)
    profile_id_index = profile_url.index('profileId=') + len('profileId=')
    return profile_url[profile_id_index:]

async def get_current_exam_period():
    '''
    Returns the start and end datetimes for the current semester's exam period.

    Note: Assumes that Semester 1 always occurs before or during June, with
    Semester 2 occurring after.
    '''
    today = datetime.today()
    current_calendar_url = BASE_CALENDAR_URL + str(today.year)
    http_response = await bot.run_async(requests.get, current_calendar_url)
    if http_response.status_code != 200:
        raise HttpException(current_calendar_url, http_response.status_code)
    html = BeautifulSoup(http_response.content, 'html.parser')
    event_date_elements = html.findAll('li', class_='description-calendar-view')
    event_date_texts = [element.text for element in event_date_elements]
    current_semester = '1' if today.month <= 6 else '2'
    current_exam_snippet = f'Semester {current_semester} examination period '
    # The first event encountered is the one which states the commencement of
    # the semester's exams and also provides the exam period.
    exam_date_text = [t[len(current_exam_snippet):] for t in event_date_texts
                      if current_exam_snippet in t][0]
    start_day, end_date = exam_date_text.split(' - ')
    end_datetime = parser.parse(end_date)
    start_datetime = end_datetime.replace(day=int(start_day))
    return start_datetime, end_datetime

async def get_parsed_assessment_due_date(assessment):
    '''
    Returns the parsed due date for the given assessment as a datetime object.
    If the date cannot be parsed, a DateSyntaxException is raised.
    '''
    _, _, due_date, _ = assessment
    if due_date == 'Examination Period':
        return await get_current_exam_period()
    try:
        day_first_info = parser.parserinfo(dayfirst=True)
        # If a date range is detected, attempt to split into start and end
        # dates. Else, attempt to just parse the whole thing.
        if ' - ' in due_date:
            start_date, end_date = due_date.split(' - ', 1)
            return (parser.parse(start_date, day_first_info),
                    parser.parse(end_date, day_first_info))
        return parser.parse(due_date, day_first_info), None
    except:
        raise DateSyntaxException(due_date)

async def is_assessment_after_cutoff(assessment, cutoff):
    '''
    Returns whether the assessment occurs after the given cutoff datetime.
    '''
    start_datetime, end_datetime = await get_parsed_assessment_due_date(assessment)
    return end_datetime >= cutoff if end_datetime else start_datetime >= cutoff

async def get_course_assessment(profile_ids, cutoff):
    '''
    Returns all the course assessment for the given course profiles that occur
    after the given cutoff datetime.
    '''
    joined_assessment_url = BASE_ASSESSMENT_URL + ','.join(profile_ids)
    http_response = await bot.run_async(requests.get, joined_assessment_url)
    if http_response.status_code != 200:
        raise HttpException(joined_assessment_url, http_response.status_code)
    html = BeautifulSoup(http_response.content, 'html.parser')
    assessment_table = html.find('table', class_='tblborder')
    assessment = assessment_table.findAll('tr')[1:]
    parsed_assessment = map(get_parsed_assessment_item, assessment)
    filtered_assessment = [a for a in parsed_assessment
                           if await is_assessment_after_cutoff(a, cutoff)]
    return filtered_assessment

def get_element_inner_html(dom_element):
    '''
    Returns the inner html for the given element.
    '''
    return dom_element.decode_contents(formatter='html')

def get_parsed_assessment_item(assessment_item):
    '''
    Returns the parsed assessment details for the given assessment item table
    row element.

    Note: Because of the inconsistency of UQ assessment details, I've had to
    make some fairly strict assumptions about the structure of each field.
    This is likely insufficient to handle every course's structure, and thus
    is subject to change.
    '''
    course, task, due_date, weight = assessment_item.findAll('div')
    # Handles courses of the form 'CSSE1001 - Sem 1 2018 - St Lucia - Internal'.
    # Thus, this bit of code will extract the course.
    course = course.text.strip().split(' - ')[0]
    # Handles tasks of the form 'Computer Exercise<br/>Assignment 2'.
    task = get_element_inner_html(task).strip().replace('<br/>', ' - ')
    # Handles due dates of the form '26 Mar 18 - 27 Mar 18<br/>Held in Week 6
    # Learning Lab Sessions (Monday/Tuesday)'. Thus, this bit of code will
    # keep only the date portion of the field.
    due_date = get_element_inner_html(due_date).strip().split('<br/>')[0]
    # Handles weights of the form '30%<br/>Alternative to oral presentation'.
    # Thus, this bit of code will keep only the weight portion of the field.
    weight = get_element_inner_html(weight).strip().split('<br/>')[0]
    return (course, task, due_date, weight)
