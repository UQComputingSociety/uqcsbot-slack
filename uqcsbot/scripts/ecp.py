from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
from uqcsbot.utils.uq_course_utils import (get_course_profile_url,
                                           HttpException,
                                           CourseNotFoundException,
                                           ProfileNotFoundException)


@bot.on_command('ecp')
@loading_status
def handle_ecp(command: Command):
    '''
    `!ecp [COURSE CODE]` - Returns the link to the latest ECP for the given
    course code. If unspecified, will attempt to find the ECP for the channel
    the command was called from.
    '''
    channel = bot.channels.get(command.channel_id)
    course_name = channel.name if not command.has_arg() else command.arg
    try:
        profile_url = get_course_profile_url(course_name)
    except HttpException as e:
        bot.logger.error(e.message)
        bot.post_message(channel, f'An error occurred, please try again.')
        return
    except (CourseNotFoundException, ProfileNotFoundException) as e:
        bot.post_message(channel, e.message)
        return
    bot.post_message(channel, f'*{course_name}*: <{profile_url}|ECP>')
