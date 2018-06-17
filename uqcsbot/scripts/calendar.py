from datetime import datetime
from icalendar import Calendar, Event
from uuid import uuid4 as uuid
from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status, success_status
from uqcsbot.utils.uq_course_utils import (get_course_assessment,
                                           get_parsed_assessment_due_date,
                                           HttpException,
                                           CourseNotFoundException,
                                           ProfileNotFoundException,
                                           DateSyntaxException)

# Maximum number of courses supported by !calendar to reduce call abuse.
COURSE_LIMIT = 6


def get_calendar(assessment):
    '''
    Returns a compiled calendar containing the given assessment.
    '''
    calendar = Calendar()
    for assessment_item in assessment:
        course, task, due_date, weight = assessment_item
        event = Event()
        event['uid'] = str(uuid())
        event['summary'] = f'{course} ({weight}): {task}'
        try:
            start_datetime, end_datetime = get_parsed_assessment_due_date(assessment_item)
        except DateSyntaxException as e:
            bot.logger.error(e.message)
            # If we can't parse a date, set its due date to today and let the
            # user know through its summary.
            # TODO(mitch): Keep track of these instances to attempt to accurately
            # parse them in future. Will require manual detection + parsing.
            start_datetime = end_datetime = datetime.today()
            event['summary'] = 'WARNING: DATE PARSING FAILED\nPlease manually' \
                               + 'set date for event!\nThe provided due date' \
                               + 'from UQ was \'{due_date}\'.' + event['summary']
        event.add('dtstart', start_datetime)
        event.add('dtend', end_datetime)
        calendar.add_component(event)
    return calendar.to_ical()


@bot.on_command('calendar')
@success_status
@loading_status
def handle_calendar(command: Command):
    '''
    `!calendar <COURSE CODE 1> [COURSE CODE 2] ...` - Returns a compiled
    calendar containing all the assessment for a given list of course codes.
    '''
    channel = bot.channels.get(command.channel_id)
    course_names = command.arg.split() if command.has_arg() else [channel.name]

    if len(course_names) > COURSE_LIMIT:
        bot.post_message(channel, f'Cannot process more than {COURSE_LIMIT} courses.')
        return

    try:
        assessment = get_course_assessment(course_names)
    except HttpException as e:
        bot.logger.error(e.message)
        bot.post_message(channel, f'An error occurred, please try again.')
        return
    except (CourseNotFoundException, ProfileNotFoundException) as e:
        bot.post_message(channel, e.message)
        return

    user_direct_channel = bot.channels.get(command.user_id)
    bot.api.files.upload(title='Importable calendar containing your assessment!',
                         channels=user_direct_channel.id, filetype='text/calendar',
                         filename='assessment.ics', file=get_calendar(assessment))
