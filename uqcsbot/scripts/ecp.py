from uqcsbot import bot, Command
from uqcsbot.scripts.uq_course_util import (get_course_profile_url,
                                            HttpException,
                                            CourseNotFoundException,
                                            ProfileNotFoundException)

@bot.on_command('ecp')
async def handle_ecp(command: Command):
    '''
    `!ecp [COURSE CODE]` - Returns the link to the latest ECP for the given
    course code. If unspecified, will attempt to find the ECP for the channel
    the command was called from.
    '''
    channel = command.channel
    course_name = channel.name if not command.has_arg() else command.arg
    try:
        profile_url = await get_course_profile_url(course_name)
    except (HttpException, CourseNotFoundException, ProfileNotFoundException) as e:
        if isinstance(e, HttpException):
            message = f'An error occurred, please try again.'
        elif isinstance(e, CourseNotFoundException):
            message = f'Could not find course `{e.course_name}`.'
        elif isinstance(e, ProfileNotFoundException):
            message = f'Could not retrieve a Profile ID for `{e.course_name}`.'
        await bot.as_async.post_message(channel, message)
        return
    await bot.as_async.post_message(channel, f'*{course_name}*: <{profile_url}|ECP>')
