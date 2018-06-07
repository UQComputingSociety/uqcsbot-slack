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
    TODO(mitch): this
    '''
    def __init__(self, date):
        super().__init__()
        self.date = date
        bot.logger.error(f'Could not parse date \'{date}\'.')

class CourseNotFoundException(Exception):
    '''
    TODO(mitch): this
    '''
    def __init__(self, course_name):
        super().__init__()
        self.course_name = course_name
        bot.logger.error(f'Could not find course \'{course_name}\'.')

class HttpException(Exception):
    '''
    TODO(mitch): this
    '''
    def __init__(self, url, status_code):
        super().__init__()
        self.url = url
        self.status_code = status_code
        bot.logger.error(f'Received status code {status_code} from \'{url}\'.')

async def get_course_profile_url(course_name):
    '''
    TODO(mitch): this
    '''
    course_url = BASE_COURSE_URL + course_name
    http_response = await bot.run_async(requests.get, course_url)
    if http_response.status_code != 200:
        raise HttpException(course_url, http_response.status_code)
    html = BeautifulSoup(http_response.content, 'html.parser')
    if html.find(id='course-notfound'):
        raise CourseNotFoundException(course_name)
    return html.find('a', class_='profile-available').get('href')

async def get_course_profile_id(course_name):
    '''
    TODO(mitch): this
    '''
    profile_url = await get_course_profile_url(course_name)
    profile_id_index = profile_url.index('profileId=') + len('profileId=')
    return profile_url[profile_id_index:]

async def get_current_exam_period():
    '''
    TODO(mitch): this
    '''
    today = datetime.today()
    current_month = today.month
    # Assuming Semester 1 always occurs before or during June and Semester 2
    # starts after.
    current_semester = '1' if current_month <= 6 else '2'
    current_year = str(today.year)
    current_calendar_url = BASE_CALENDAR_URL + current_year
    http_response = await bot.run_async(requests.get, current_calendar_url)
    if http_response.status_code != 200:
        raise HttpException(current_calendar_url, http_response.status_code)
    html = BeautifulSoup(http_response.content, 'html.parser')
    event_date_elements = html.findAll('li', class_='description-calendar-view')
    event_date_texts = [element.text for element in event_date_elements]
    current_exam_snippet = f'Semester {current_semester} examination period '
    # First event is stating the commencement of exams and provides the dates
    exam_date_text = [t[len(current_exam_snippet):] for t in event_date_texts
                      if current_exam_snippet in t][0]
    start_day, end_date = exam_date_text.split(' - ')
    end_datetime = parser.parse(end_date)
    start_datetime = end_datetime.replace(day=int(start_day))
    return start_datetime, end_datetime

async def get_assessment_datetime(assessment):
    '''
    TODO(mitch): this
    '''
    _, _, due_date, _ = assessment
    # TODO(mitch): explain each method. Returns a start datetime and end datetime
    if due_date == 'Examination Period':
        return await get_current_exam_period()
    try:
        day_first_info = parser.parserinfo(dayfirst=True)
        if ' - ' in due_date:
            start_date, end_date = due_date.split(' - ', 1)
            return (parser.parse(start_date, day_first_info),
                    parser.parse(end_date, day_first_info))
        return parser.parse(due_date, day_first_info), None
    except:
        raise DateSyntaxException(due_date)

async def is_assessment_before_cutoff(assessment, cutoff):
    '''
    TODO(mitch): this
    '''
    start_datetime, end_datetime = await get_assessment_datetime(assessment)
    return end_datetime >= cutoff if end_datetime else start_datetime >= cutoff

async def get_course_assessment(profile_ids, cutoff):
    '''
    TODO(mitch): this. Talk about cutoff behaviour
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
                           if await is_assessment_before_cutoff(a, cutoff)]
    return filtered_assessment

def get_element_inner_html(dom_element):
    '''
    TODO(mitch): this
    '''
    return dom_element.decode_contents(formatter='html')

def get_parsed_assessment_item(assessment_item):
    '''
    TODO(mitch): this. explain assumptions
    '''
    course, task, due_date, weight = assessment_item.findAll('div')
    course = course.text.strip().split(' - ')[0]
    task = get_element_inner_html(task).strip().replace('<br/>', ' - ')
    due_date = get_element_inner_html(due_date).strip().split('<br/>')[0]
    weight = get_element_inner_html(weight).strip().split('<br/>')[0]
    return (course, task, due_date, weight)
