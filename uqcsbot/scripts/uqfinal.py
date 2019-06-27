from math import ceil
from uqcsbot import bot, Command
from requests import get, RequestException, Response
from typing import List
from uqcsbot.utils.command_utils import loading_status

UQFINAL_API = "https://api.uqfinal.com"


@bot.on_command("uqfinal")
@loading_status
def handle_uqfinal(command: Command):
    """
    `!uqfinal <CODE> <GRADES>` - Check UQFinal for course CODE
    with the first assessments pieces as <GRADES> as percentages
    """
    # Makes sure the query is not empty
    if not command.has_arg():
        bot.post_message(command.channel_id, "Please choose a course")
        return

    args = command.arg.split()

    course = args[0]  # Always exists
    arg_scores = args[1:]
    scores: List[float] = []

    # get UQ Final data
    semester = get_uqfinal_semesters()
    if semester is None:
        bot.post_message(command.channel_id, "Failed to retrieve semester data from UQfinal")
        return

    course_info = get_uqfinal_course(semester, course)
    if course_info is None:
        bot.post_message(command.channel_id, f"Failed to retrieve course information for {course}")
        return
    assessments = course_info["assessment"]

    # if no results submitted
    if not arg_scores:
        message = [f"{course.upper()} has the following assessments:"]
        for i, assess in enumerate(assessments):
            message.append(f"{i+1}: {assess['taskName']} ({assess['weight']}%)")
        message.append("_Powered by http://uqfinal.com_")
        bot.post_message(command.channel_id, "\n".join(message))
        return

    # convert arugments to decimals
    for arg_score in arg_scores:
        try:
            score = float(arg_score.rstrip("%"))
        except ValueError:
            bot.post_message(command.channel_id,
                             f"\"{arg_score}\" could not be converted to a number.")
            return
        score_deci = score / (100 if score > 1 else 1)
        if score_deci < 0 or score_deci > 1:
            bot.post_message(command.channel_id,
                             "Assessments scores should be between 0% and 100%.")
            return
        scores.append(score_deci)

    # if too many results
    if len(scores) >= len(assessments):
        bot.post_message(command.channel_id,
                         f"Too many retults provided.\n"
                         f"This course has {len(assessments)} assessments.")
        return

    # calculate achived marks
    total_deci = 0.0
    results = []
    for i, score_deci in enumerate(scores):
        total_deci += score_deci * float(assessments[i]["weight"]) / 100
        results.append(f"Inputted score of {round(score_deci * 100)}% for"
                       f" {assessments[i]['taskName']} (weighted {assessments[i]['weight']}%)")
    bot.post_message(command.channel_id, "\n".join(results))

    # calculate remaining marks
    remain_deci = 0.0
    for i in range(len(scores), len(assessments)):
        remain_deci += float(assessments[i]["weight"]) / 100

    # calculate marks needed to achieve grades
    message = []
    for cutoff_deci, grade in [(0.5, 'four'), (0.65, 'five'), (0.75, 'six'), (0.85, 'seven')]:
        needed_perc = ceil(100 * (cutoff_deci - total_deci) / remain_deci)
        if needed_perc > 100:
            break
        if needed_perc <= 0:
            message.append(f"You have achieved a {grade} :toot:.")
        elif len(scores) == len(assessments) - 1:
            message.append(f"You need to score at least {needed_perc}%"
                           f" on the {assessments[-1]['taskName']} to achieve a {grade}.")
        else:
            message.append(f"You need to score at least a weighted average of {needed_perc}%"
                           f" on the remaining {len(assessments) - len(scores)}"
                           f" assessments to achieve a {grade}.")

    # if getting a four impossible
    if not message:
        message.append("I am a servant of the Secret Fire, wielder of the flame of Anor."
                       " The dark fire will not avail you, flame of Udûn. Go back to the Shadow!"
                       " *You cannot pass.*")
    message.append("_Disclaimer: this does not take hurdles into account._")
    message.append("_Powered by http://uqfinal.com_")
    bot.post_message(command.channel_id, "\n".join(message))


def get_uqfinal_semesters():
    """
    Get the current semester data from uqfinal
    Return None on failure
    """
    try:
        # Assume current semester
        semester_response: Response = get(UQFINAL_API + "/semesters")
        if semester_response.status_code != 200:
            bot.logger.error(f"UQFinal returned {semester_response.status_code}"
                             f" when getting the current semester")
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
        course_response = get("/".join([UQFINAL_API, "course", str(semester["uqId"]), course]))
        if course_response.status_code != 200:
            bot.logger.error(f"UQFinal returned {course_response.status_code}"
                             f" when getting the course {course}")
            return None
        return course_response.json()["data"]
    except RequestException as e:
        bot.logger.error(f"A request error {e.response.status} occurred:\n{e.response.content}")
        return None
