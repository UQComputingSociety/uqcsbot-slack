from uqcsbot import bot
import requests
from bs4 import BeautifulSoup

COURSE_URL = 'https://my.uq.edu.au/programs-courses/course.html?course_code='
ASSESSMENT_URL = 'https://www.courses.uq.edu.au/student_section_report.php?report=assessment&profileIds='

async def get_course_profile_url(course_name):
    '''
    TODO(mitch): this
    '''
    http_response = await bot.run_async(requests.get, COURSE_URL + course_name)
    html = BeautifulSoup(http_response.content, 'html.parser')
    if html.find(id='course-notfound'):
        return None
    return html.find('a', class_='profile-available').get('href')

async def get_course_profile_id(course_name):
    '''
    TODO(mitch): this
    '''
    profile_url = await get_course_profile_url(course_name)
    if profile_url is None:
        return None
    profile_id_index = profile_url.index('profileId=') + len('profileId=')
    return profile_url[profile_id_index:]

async def get_course_assessment(profile_ids):
    '''
    TODO(mitch): this
    '''
    joined_assessment_url = ASSESSMENT_URL + ','.join(profile_ids)
    http_response = await bot.run_async(requests.get, joined_assessment_url)
    html = BeautifulSoup(http_response.content, 'html.parser')
    assessment_table = html.find('table', class_='tblborder')
    if assessment_table is None:
        return None
    assessment = assessment_table.findAll('tr')[1:]
    return list(map(get_parsed_assessment_item, assessment))

def get_inner_html(dom_element):
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
    task = get_inner_html(task).strip().replace('<br/>', ' - ')
    due_date = get_inner_html(due_date).strip().split('<br/>')[0]
    weight = get_inner_html(weight).strip().split('<br/>')[0]
    return (course, task, due_date, weight)
