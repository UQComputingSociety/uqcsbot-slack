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

    course = args[0]  # Always exists
    string_scores = args[1:]
    scores = []

    for score in string_scores:
        try:
            scores.append(float(score))
        except:
            bot.post_message(command.channel_id, f"{score} could not be converted to a number")

    semester = get_uqfinal_semesters()
    if semester == None:
        bot.post_message("Failed to retrieve semester data from UQfinal")
        return

    courseInfo = get_uqfinal_course(semester, course)
    if courseInfo == None:
        bot.post_message(f"Failed to retrieve course information for {course}")
    num_assessment = len(courseInfo["assessment"])

    if (len(scores) != num_assessment - 1):
        bot.post_message(command.channel_id, "Please provide grades for all assessment except the last")
        return

    total = 0
    for i, score in enumerate(scores):
        total += score * float(courseInfo["assessment"][i]["weight"]) / 100

    needed = 50 - total
    result = math.ceil(needed / float(courseInfo["assessment"][num_assessment - 1]["weight"]) * 100)
    bot.post_message(command.channel_id, "You need to achieve at least " +
                     str(result) +
                     "% on the final exam.\n_Disclaimer: this does not take hurdles into account_\n_Powered by "
                     "http://uqfinal.com_")


def get_uqfinal_semesters():
    """
    Get the current semester data from uqfinal
    Return None on failure
    """
    try:
        # Assume current semester
        semesterResponse = get(uqfinal + "/semesters")
        return semesterResponse.json()["data"]["semesters"].pop()
    except RequestException as e:
        bot.logger.error(f"A request error {e.resp.status} occurred:\n{e.content}")
        return None


def get_uqfinal_course(semester, course: str):
    """
    Get the current course data from uqfinal
    Return None on failure
    """
    try:
        courseResponse = get("/".join([uqfinal, "course", str(semester["uqId"]), course]))
        return courseResponse.json()["data"]
    except RequestException as e:
        bot.logger.error(f"A request error {e.resp.status} occurred:\n{e.content}")
        return None
