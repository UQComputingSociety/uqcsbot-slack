from datetime import datetime
from uqcsbot import bot, Command
from uqcsbot.scripts.uq_course_util import (get_course_profile_id,
                                            get_course_assessment,
                                            HttpException,
                                            CourseNotFoundException,
                                            ProfileNotFoundException)

def get_formatted_assessment_item(assessment_item):
    '''
    TODO(mitch): this
    '''
    course, task, due, weight = assessment_item
    return f'*{course}*: `{weight}` _{task}_ *({due})*'

@bot.on_command('whatsdue')
async def handle_whatsdue(command: Command):
    '''
    TODO(mitch): helper doc. Talk about is_full_output behaviour
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

    course_limit = 6
    if len(course_names) > course_limit:
        error_message = f'Cannot process more than {course_limit} courses.'
        await bot.as_async.post_message(channel, error_message)
        return

    try:
        profile_ids = [await get_course_profile_id(name) for name in course_names]
    except HttpException as e:
        error_message = f'An error occurred, please try again.'
        await bot.as_async.post_message(channel, error_message)
        return
    except CourseNotFoundException as e:
        error_message = f'Could not find course `{e.course_name}`.'
        await bot.as_async.post_message(channel, error_message)
        return
    except ProfileNotFoundException as e:
        error_message = f'Could not retrieve a Profile ID for `{e.course_name}`.'
        await bot.as_async.post_message(channel, error_message)
        return

    cutoff_datetime = datetime.today()
    if is_full_output:
        cutoff_datetime = datetime.fromtimestamp(0)

    try:
        assessment = await get_course_assessment(profile_ids, cutoff_datetime)
    except HttpException as e:
        error_message = f'TODO(mitch): this (http exception)'
        await bot.as_async.post_message(channel, error_message)
        return

    message = '_*WARNING:* Assessment information may vary/change/be entirely' \
               + ' different! Use at your own discretion_\n>>>'
    message += '\n'.join(map(get_formatted_assessment_item, assessment))
    await bot.as_async.post_message(channel, message)
