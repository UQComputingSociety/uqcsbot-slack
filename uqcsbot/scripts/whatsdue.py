from datetime import datetime
from uqcsbot import bot, Command
from uqcsbot.scripts.uq_course_util import (get_course_profile_id,
                                            get_course_assessment,
                                            HttpException,
                                            CourseNotFoundException,
                                            ProfileNotFoundException)

def get_formatted_assessment_item(assessment_item):
    '''
    Returns the given assessment item in a pretty message format to display to
    a user.
    '''
    course, task, due, weight = assessment_item
    return f'*{course}*: `{weight}` _{task}_ *({due})*'

@bot.on_command('whatsdue')
async def handle_whatsdue(command: Command):
    '''
    `!whatsdue [-f] [--full] [COURSE CODE 1] [COURSE CODE 2] ...` - Returns all
    the assessment for a given list of course codes that are scheduled to occur
    after today. If unspecified, will attempt to return the assessment for the
    channel that the command was called from. If -f/--full is provided, will
    return the full assessment list without filtering by cutoff dates.
    '''
    channel = command.channel
    course_names = command.arg.split() if command.has_arg() else [channel.name]

    is_full_output = False
    if '--full' in course_names:
        course_names.remove('--full')
        is_full_output = True
    if '-f' in course_names:
        course_names.remove('-f')
        is_full_output = True
    # If unspecified, set the cutoff to today's date. Else, set the cutoff to
    # UNIX epoch (i.e. filter nothing).
    cutoff_datetime = datetime.today()
    if is_full_output:
        cutoff_datetime = datetime.fromtimestamp(0)

    course_limit = 6
    if len(course_names) > course_limit:
        error_message = f'Cannot process more than {course_limit} courses.'
        await bot.as_async.post_message(channel, error_message)
        return

    try:
        assessment = await get_course_assessment(course_names, cutoff_datetime)
    except (HttpException, CourseNotFoundException, ProfileNotFoundException) as e:
        if isinstance(e, HttpException):
            message = f'An error occurred, please try again.'
        elif isinstance(e, CourseNotFoundException):
            message = f'Could not find course `{e.course_name}`.'
        elif isinstance(e, ProfileNotFoundException):
            message = f'Could not retrieve a Profile ID for `{e.course_name}`.'
        await bot.as_async.post_message(channel, message)
        return

    message = '_*WARNING:* Assessment information may vary/change/be entirely' \
               + ' different! Use at your own discretion_\n>>>'
    message += '\n'.join(map(get_formatted_assessment_item, assessment))
    if not is_full_output:
        message += '\n_Note: This may not be the full assessment list. Use -f' \
                   + '/--full to print out the full list._'
    await bot.as_async.post_message(channel, message)
