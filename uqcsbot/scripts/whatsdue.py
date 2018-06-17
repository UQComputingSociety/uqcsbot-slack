import argparse
from datetime import datetime
from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status, UsageSyntaxException
from uqcsbot.utils.uq_course_utils import (get_course_assessment,
                                           HttpException,
                                           CourseNotFoundException,
                                           ProfileNotFoundException)

# Maximum number of courses supported by !whatsdue to reduce call abuse.
COURSE_LIMIT = 6


def get_formatted_assessment_item(assessment_item):
    '''
    Returns the given assessment item in a pretty message format to display to
    a user.
    '''
    course, task, due, weight = assessment_item
    return f'*{course}*: `{weight}` _{task}_ *({due})*'


@bot.on_command('whatsdue')
@loading_status
def handle_whatsdue(command: Command):
    '''
    `!whatsdue [-f] [--full] [COURSE CODE 1] [COURSE CODE 2] ...` - Returns all
    the assessment for a given list of course codes that are scheduled to occur
    after today. If unspecified, will attempt to return the assessment for the
    channel that the command was called from. If `-f`/`--full` is provided, will
    return the full assessment list without filtering by cutoff dates.
    '''
    channel = bot.channels.get(command.channel_id)
    command_args = command.arg.split() if command.has_arg() else []

    arg_parser = argparse.ArgumentParser()
    def usage_error(*args, **kwargs):
        raise UsageSyntaxException()
    arg_parser.error = usage_error  # type: ignore
    arg_parser.add_argument('-f', '--full', action='store_true')
    arg_parser.add_argument('course_codes', nargs='*')

    parsed_args = arg_parser.parse_args(command_args)
    course_names = parsed_args.course_codes if len(parsed_args.course_codes) > 0 else [channel.name]
    if len(course_names) > COURSE_LIMIT:
        bot.post_message(channel, f'Cannot process more than {COURSE_LIMIT} courses.')
        return

    # If full output is not specified, set the cutoff to today's date.
    cutoff = None if parsed_args.full else datetime.today()
    try:
        assessment = get_course_assessment(course_names, cutoff)
    except HttpException as e:
        bot.logger.error(e.message)
        bot.post_message(channel, f'An error occurred, please try again.')
        return
    except (CourseNotFoundException, ProfileNotFoundException) as e:
        bot.post_message(channel, e.message)
        return

    message = '_*WARNING:* Assessment information may vary/change/be entirely' \
              + ' different! Use at your own discretion_\n>>>'
    message += '\n'.join(map(get_formatted_assessment_item, assessment))
    if not parsed_args.full:
        message += '\n_Note: This may not be the full assessment list. Use -f' \
                   + '/--full to print out the full list._'
    bot.post_message(channel, message)
