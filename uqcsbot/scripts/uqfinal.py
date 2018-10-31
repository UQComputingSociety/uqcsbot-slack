import math
from uqcsbot import bot, Command
from requests import get
from uqcsbot.utils.command_utils import loading_status

uqfinal = "https://api.uqfinal.com"

@bot.on_command("uqfinal")
@loading_status
def handle_uqfinal(command: Command):
    """
    `!uqfinal <CODE> <GRADES>` - Check UQFinal for course CODE with the first assessment pieces as <GRADES> as percentages
    """
    # Makes sure the query is not empty
    if not command.has_arg():
        bot.post_message(command.channel_id, "Please choose a course")
        return
    
    args = command.arg.split()
    
    course = args[0] # Always exists
    string_scores = args[1:]
    scores = []

    for score in string_scores:
        try:
            scores.append(int(score))
        except:
            bot.post_message(command.channel_id, score + " could not be converted to a score")


    # Assume current semester
    semesterResponse = get(uqfinal + "/semesters")
    semester = semesterResponse.json()["semesters"].pop()

    courseResponse = get("/".join([uqfinal, course, semester["uqId"]]))
    courseInfo = courseResponse.json()

    num_assessment = len(courseInfo["assessment"])

    if (len(scores) != num_assessment - 1):
        bot.post_message(command.channel_id, "Please provide grades for all assessment except the last")
        return

    total = 0
    for i, score in enumerate(scores):
        total += score * courseInfo["assessment"][i].weight

    needed = 50 - total
    result = math.ceil(needed / course.assessment[num_assessment - 1].weight * 100)
    bot.post_message(command.channel_id, "You need to achieve at least " +
                     str(result) +
                     "% on the final exam.\n_Disclaimer: this does not take hurdles into account_\n_Powered by "
                     "http://uqfinal.com_")
