import math
from uqcsbot import bot, Command
from requests import get, RequestException, Response
from typing import List
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
    scores: List[float] = []

    for str_score in string_scores:
        try:
            temp = float(str_score)
            if temp <= 1:
                bot.post_message(command.channel_id, f"Note: Treating {str_score} as {temp * 100}%")
                temp *= 100
            if temp < 0 or temp > 100:
                bot.post_message(command.channel_id, f"Assessment scores should be between 0 and 100")
                return
            scores.append(temp)
        except ValueError:
            bot.post_message(command.channel_id, f"\"{str_score}\" could not be converted to a number")
            return

    semester = get_uqfinal_semesters()
    if semester == None:
        bot.post_message(command.channel_id, "Failed to retrieve semester data from UQfinal")
        return

    course_info = get_uqfinal_course(semester, course)
    if course_info == None:
        bot.post_message(command.channel_id, f"Failed to retrieve course information for {course}")
        return
    num_assessment = len(course_info["assessment"])

    if (len(scores) != num_assessment - 1):
        bot.post_message(command.channel_id, f"Please provide grades for all assessment except the last\nThis course has {num_assessment} assessments")
        return

    total = 0.0
    for i, score in enumerate(scores):
        total += score * float(course_info["assessment"][i]["weight"]) / 100

    needed = 50 - total
    result = math.ceil(needed / float(course_info["assessment"][num_assessment - 1]["weight"]) * 100)
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
        semester_response: Response = get(uqfinal + "/semesters")
        if semester_response.status_code != 200:
            bot.logger.error(f"UQFinal returned {semester_response.status_code} when getting the current semester")
            return None
        return semester_response.json()["data"]["semesters"].pop()
    except RequestException as e:
        bot.logger.error(f"A request error {e.response.status} occurred:\n{e.response.content}")
        return None


def get_uqfinal_course(semester, course: str):
    """
    Get the current course data from uqfinal
    Return None on failure
    """
    try:
        course_response = get("/".join([uqfinal, "course", str(semester["uqId"]), course]))
        if course_response.status_code != 200:
            bot.logger.error(f"UQFinal returned {course_response.status_code} when getting the course {course}")
            return None
        return course_response.json()["data"]
    except RequestException as e:
        bot.logger.error(f"A request error {e.response.status} occurred:\n{e.response.content}")
        return None
