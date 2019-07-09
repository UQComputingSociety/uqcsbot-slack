from uqcsbot import bot, Command

RESPONSE = ("*Mental health/crisis resources*\n"
            "24/7 UQ Counselling and Crisis Line: 1300 851 998\n"
            "Campus Security (emergency): 07 3365 3333\n"
            "Campus Security (non-emergency): 07 3365 1234\n"
            "Counselling Services: https://www.uq.edu.au/student-services/counselling-services\n"
            "UQ Psychology Clinic: https://clinic.psychology.uq.edu.au/therapies-and-services\n"
            "UQ resources: https://about.uq.edu.au/campaigns-and-initiatives/mental-health")


@bot.on_command("crisis")
@bot.on_command("mentalhealth")
@bot.on_command("emergency")
def handle_crisis(command: Command):
    """
    `!crisis`, `!mentalhealth` or `!emergency` - Get a list of emergency resources.
    """

    bot.post_message(command.channel_id, RESPONSE)
