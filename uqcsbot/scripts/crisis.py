from uqcsbot import bot, Command


@bot.on_command("crisis")
@bot.on_command("mentalhealth")
def handle_crisis(command: Command):
    '''
    `!crisis` or `!mentalhealth` - Get a list of mental health crisis resources.
    '''
    response = """*Mental health/crisis resources*
24/7 UQ Counselling and Crisis Line: 1300 851 998
Campus Security (emergency): 07 3365 3333
Campus Security (non-emergency): 07 3365 1234
Counselling Services: https://www.uq.edu.au/student-services/counselling-services
UQ Psychology Clinic: https://clinic.psychology.uq.edu.au/therapies-and-services
UQ resources: https://about.uq.edu.au/campaigns-and-initiatives/mental-health"""

    bot.post_message(command.channel_id, response)
