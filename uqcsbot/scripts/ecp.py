from uqcsbot import bot, Command
from uqcsbot.scripts.uq_course_util import (get_course_profile_url,
                                            HttpException,
                                            CourseNotFoundException,
                                            ProfileNotFoundException)

@bot.on_command('ecp')
def handle_ecp(command: Command):
    '''
    `!ecp [COURSE CODE]` - Returns the link to the latest ECP for the given
    course code. If unspecified, will attempt to find the ECP for the channel
    the command was called from.
    '''
    channel = command.channel
    course_name = channel.name if not command.has_arg() else command.arg
    try:
        profile_url = get_course_profile_url(course_name)
    except HttpException as e:
        bot.post_message(channel, f'An error occurred, please try again.')
        return
    except CourseNotFoundException as e:
        bot.post_message(channel, f'Could not find course `{e.course_name}`.')
        return
    except ProfileNotFoundException as e:
        bot.post_message(channel, f'Could not retrieve profile for `{e.course_name}`.')
        return
    bot.post_message(channel, f'*{course_name}*: <{profile_url}|ECP>')
