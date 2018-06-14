from uqcsbot import bot, Command
from uqcsbot.util.status_reacts import loading_status
from typing import List
import os
import re
import requests


BASE_FOLDER_URL = 'https://drive.google.com/drive/folders/'
BASE_FILE_URL = 'https://drive.google.com/file/d/'
BASE_API_URL = 'https://www.googleapis.com/drive/v3/'
BASE_ATTIC_FOLDER = '0B6_D4T6LJ-uwZmFhMzIyNGYtNTM2OS00ZDJlLTg0NmYtY2IyNzA1MDZlNDIx'
API_KEY = os.environ['GOOGLE_API_KEY']
ROOM_FILE_LIMIT = 15  # Number of files allowed to be posted in room, else sent via direct message.
SLACK_MAX_LINES = 45  # Slack appears to split messages past this point.
COURSE_REGEX = r'[A-Z]{4}[1-7]{1}[0-9]{3}'


def format_files(files: List[dict], course: dict) -> List[str]:
    """
    Takes the list of file dictionaries found and formats them into Slack-appropriate message strings.
    :param files: a list of dictionaries where each dictionary represents a file in the Google Drive folder.
    :param course: a dictionary representing the parent Google Drive folder for the queried course.
    :return: a list of strings to be sent as messages.
    """
    sorted_files = sorted(files, key=lambda f: f['name'])  # Sort alphabetically by filename.
    response = [f'All of the UQAttic files for the course <{BASE_FOLDER_URL}{course["id"]} | {course["name"]}> are '
                f'included below:\n>>> ']
    # Handle formatting for long messages where Slack would otherwise split them.
    line_count = 0
    for file in sorted_files:
        file_string = f'*{file["name"]}:* <{BASE_FILE_URL}{file["id"]}|Link>\n'
        if line_count < SLACK_MAX_LINES:
            line_count += 1
            response[-1] += file_string
        else:
            line_count = 0
            response.append('>>>' + file_string)
    return response


def get_all_files(file: dict) -> List[dict]:
    """
    Takes a parent folder and recursively produces a single-level list of all files contained in it and any
    subdirectories.
    :param file: a dictionary representing the parent Google Drive folder.
    :return: a single-dimensional list of file dictionaries.
    """
    files = []
    if file['mimeType'] == 'application/vnd.google-apps.folder':
        contents = get_folder_contents(file)
        for subfile in contents:
            files += get_all_files(subfile)
    else:
        files.append(file)
    return files


def get_folder_contents(folder: dict) -> List[dict]:
    """
    Gets all files and folders inside the given Google Drive folder dictionary.
    N.B: does not return the contents of subdirectories.
    :param folder: a dictionary representing a Google Drive folder to get the contents of.
    :return: a list of Google drive folder/file dictionaries representing all contents of the folder.
    """
    folder_url = f"{BASE_API_URL}files?q='{folder['id']}' in parents&key={API_KEY}"
    http_response = requests.get(folder_url)
    if http_response.status_code == 200:
        return http_response.json()['files']
    else:
        raise ValueError(f"There was an error getting the contents of folder: {folder['name']}")


@bot.on_command('attic')
@loading_status
def handle_attic(command: Command) -> None:
    """
    `!attic [COURSE CODE]` - Returns a list of links to all documents in the course folder for UQ Attic, the unofficial
    exam solution and study material repository. Defaults to searching for the name of the current channel unless
    explicitly provided a course code (e.g. CSSE1001).
    """
    if command.has_arg():
        course_code = command.arg  # Get course code if given.
    else:
        course_code = command.channel.name  # Default to channel if not given.
    course_code = course_code.upper()

    # Check course code is valid before making request
    if not re.fullmatch(COURSE_REGEX, course_code):
        bot.post_message(command.channel, "Invalid course code.")
        return

    # Make request for UQAttic root folder
    base_folder_request_url = f"{BASE_API_URL}files?q='{BASE_ATTIC_FOLDER}' in parents and mimeType = 'application/" \
                              f"vnd.google-apps.folder'&pageSize=1000&key={API_KEY}"
    root = requests.get(base_folder_request_url)
    if root.status_code == 200:
        try:
            root_data = root.json()
        except ValueError:
            bot.post_message(command.channel, 'There was an error getting the base UQAttic folder.\n')
            return
    else:
        bot.post_message(command.channel, 'There was an error getting the base UQAttic folder.')
        return

    # Check course folder exists
    course = next((item for item in root_data['files'] if item['name'] == course_code), None)
    if course is None:
        bot.post_message(command.channel, 'No course folder found for ' + course_code + '.')
        return

    # Get all files
    files = get_all_files(course)

    # Determine whether to send to user or channel (based on number of responses)
    if len(files) > ROOM_FILE_LIMIT:
        bot.post_message(command.channel, f'Too many files to list here, sent the list directly to '
                                          f'<@{command.user_id}>.')
        response_channel = command.user_id
    else:
        response_channel = command.channel

    # Send response message with formatted list of files
    response_messages = format_files(files, course)
    for message in response_messages:
        bot.post_message(response_channel, message)

