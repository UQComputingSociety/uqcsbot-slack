from uqcsbot import bot, Command
from bs4 import BeautifulSoup
from typing import Iterable, Tuple
import requests
from uqcsbot.util.status_reacts import loading_status


@bot.on_command('pastexams')
@loading_status
def handle_pastexams(command: Command):
    '''
    `!pastexams [COURSE CODE]` - Retrieves past exams for a given course code.
    If unspecified, will attempt to find the ECP for the channel the command was
    called from.
    '''
    course_code = command.arg if command.has_arg() else command.channel.name
    bot.post_message(command.channel, get_past_exams(course_code))

def get_exam_data(soup: BeautifulSoup) -> Iterable[Tuple[str, str]]:
    """
    Takes the soup object of the page and generates each result in the format:
    ('year Sem X:', link)
    """

    # The exams are stored in a table with the structure:
    # Row 1: A bunch of informational text
    # Row 2: Semester information
    # Row 3: Links to Exams
    # Rows two and three are what we care about. Of those the first column is just a row title so we ignore that as well

    exam_table_rows = soup.find('table', class_='maintable').contents
    semesters = exam_table_rows[1].find_all('td')[1:]  # All columns in row 2 excluding the first
    # Gets the content from each td. Text is separated by a <br/> thus result is in the format (year, <br/>, 'Sem.x'
    semesters = [semester.contents for semester in semesters]

    # Same thing but for links
    links = exam_table_rows[2].find_all('td')[1:]
    links = [link.find('a')['href'] for link in links]

    for (year, _, semester_id), link in zip(semesters, links):
        semester_str = semester_id.replace('.', ' ')
        yield f'{year} {semester_str}', link

def get_past_exams(course_code: str) -> str:
    """
    Gets the past exams for the course with the specified course code. Returns intuitive error messages if this fails.
    """
    url = 'https://www.library.uq.edu.au/exams/papers.php?'
    http_response = requests.get(url, params={'stub': course_code})

    if http_response.status_code != requests.codes.ok:
        return "There was a problem getting a response"

    # Check if the course code exists
    soup = BeautifulSoup(http_response.content, 'html.parser')
    no_course = soup.find('div', class_='page').find('div').contents[0]
    if "Sorry. We have not found any past exams for this course" in no_course:
        return f"The course code {course_code} did not return any results"

    return '>>>' + '\n'.join((f'*{semester}*: <{link}|PDF>'
                              for semester, link in get_exam_data(soup)))
