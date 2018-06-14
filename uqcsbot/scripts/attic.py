from uqcsbot import bot, Command
from uqcsbot.util.status_reacts import loading_status
from typing import List
import os
import requests


BASE_FOLDER_URL = 'https://drive.google.com/drive/folders/'
BASE_FILE_URL = 'https://drive.google.com/file/d/'
BASE_API_URL = 'https://www.googleapis.com/drive/v3/'
BASE_ATTIC_FOLDER = '0B6_D4T6LJ-uwZmFhMzIyNGYtNTM2OS00ZDJlLTg0NmYtY2IyNzA1MDZlNDIx'
API_KEY = os.environ['GOOGLE_API_KEY']
ROOM_FILE_LIMIT = 15  # Number of files allowed to be posted in room, else sent via direct message.


def format_files(files: List[dict]) -> List[str]:
    """
    Takes the list of file dictionaries found and formats them into Slack-appropriate message strings.
    :param files: a list of dictionaries where each dictionary represents a file in the Google Drive folder.
    :param course: a dictionary representing the parent Google Drive folder for the queried course.
    :return: a list of strings to be sent as messages.
    """
    sorted_files = sorted(files, key=lambda f: f['name'])  # Sort alphabetically by filename.
    return [f'>*{file["name"]}:* <{BASE_FILE_URL}{file["id"]}|Link>' for file in sorted_files]


def get_all_files(folder: dict) -> List[dict]:
    """
    Takes a parent folder and recursively produces a single-level list of all files contained in that folder and any
    subdirectories.
    :param folder: a dictionary representing a Google Drive folder.
    :return: a single-dimensional list of file dictionaries.
    """
    files = []
    for file in get_folder_contents(folder):
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            files.extend(get_all_files(file))
        else:
            files.append(file)
    return files


def get_folder_contents(folder: dict) -> List[dict]:
    """
    Gets all files and folders inside the given Google Drive folder dictionary.
    Note: does not return the contents of subdirectories.
    :param folder: a dictionary representing a Google Drive folder to get the contents of.
    :return: a list of Google drive folder/file dictionaries representing all contents of the folder.
    """
    folder_url = f"{BASE_API_URL}files?q='{folder['id']}' in parents&key={API_KEY}"
    http_response = requests.get(folder_url)
    if http_response.status_code == 200:
        return http_response.json()['files']
    else:
        return []  # I figure it's better to ignore a failed folder fetch than provide no response/error out.


@bot.on_command('attic')
@loading_status
def handle_attic(command: Command) -> None:
    """
    `!attic [COURSE CODE]` - Returns a list of links to all documents in the course folder for UQ Attic, the unofficial
    exam solution and study material repository. Defaults to searching for the name of the current channel unless
    explicitly provided a course code (e.g. CSSE1001).
    """
    course_code = command.arg if command.has_arg() else command.channel.name
    course_code = course_code.upper()

    # Make request for UQAttic root directory contents.
    root_directory_request_url = f"{BASE_API_URL}files?q='{BASE_ATTIC_FOLDER}' in parents and mimeType = 'application/" \
                                 f"vnd.google-apps.folder'&pageSize=1000&key={API_KEY}"
    root_directory = requests.get(root_directory_request_url)
    if not root_directory.status_code == 200:
        bot.post_message(command.channel, 'There was an error getting the root UQAttic directory.')
        return
    root_directory_data = root_directory.json()

    # Check course folder exists by checking for the course code in the 'name' of each file/folder.
    course = next((item for item in root_directory_data['files'] if item['name'] == course_code), None)
    if course is None:
        bot.post_message(command.channel, f'No course folder found for {course_code}.')
        return

    # Get all files in directory and subdirectories.
    files = get_all_files(course)

    # Determine whether to send to user or channel (based on number of responses).
    if len(files) > ROOM_FILE_LIMIT:
        bot.post_message(command.channel, f'Too many files to list here, sent the list directly to '
                                          f'<@{command.user_id}>.')
        response_channel = command.user_id
    else:
        response_channel = command.channel

    # Send response message with formatted list of files.
    if len(files) > 0:
        response_message = f'All of the UQAttic files found for the course <{BASE_FOLDER_URL}{course["id"]} | ' \
                           f'{course["name"]}> are listed below:\n' + '\n'.join(format_files(files))
    else:
        response_message = f'There were no files found in the {course_code} course folder.'
    bot.post_message(response_channel, response_message)
