from uqcsbot import bot, Command
from uqcsbot.scripts.uq_course_util import get_course_profile_id, get_course_assessment

def get_formatted_assessment_item(assessment_item):
    '''
    TODO(mitch): this
    '''
    course, task, due, weight = assessment_item
    return f'*{course}*: `{weight}` _{task}_ *({due})*'

@bot.on_command('whatsdue')
async def handle_whatsdue(command: Command):
    '''
    TODO(mitch): helper doc
    '''
    # TODO(mitch): limit number of courses to 5
    # TODO(mitch): add cli command that ignores assessment before today
    channel = command.channel
    course_names = command.arg.split() if command.has_arg() else [channel.name]
    profile_ids = [await get_course_profile_id(name) for name in course_names]
    # TODO(mitch): explain below section, or think of something better
    for i, profile_id in enumerate(profile_ids):
        if profile_id is not None:
            continue
        bot.post_message(channel, f'Could not retrieve a Profile ID for `{course_names[i]}`.')
        return
    assessment = await get_course_assessment(profile_ids)
    message = '_*WARNING:* Assessment information may vary/change/be entirely' \
               + ' different! Use at your own discretion_\n>>>'
    message += '\n'.join(map(get_formatted_assessment_item, assessment))
    bot.post_message(channel, message)
