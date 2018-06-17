import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import UsageSyntaxException, loading_status

YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v='
NO_QUERY_MESSAGE = "You can't look for nothing. !yt <QUERY>"


def get_top_video_result(search_query: str):
    '''
    The normal method for using !yt searches based on query and returns the
    first video result akin to a "I'm feeling lucky" search.
    '''
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=YOUTUBE_API_KEY)

    search_response = youtube.search().list(
        q=search_query,
        part='id',  # Only the video ID is needed to get video link
        maxResults=1,  # Since only one video is linked this is the only result we need
        type='video'  # Only want videos no pesky channels or playlists
    ).execute()

    search_result = search_response.get('items')
    if search_result is None:
        return None
    return search_result[0]['id']['videoId']


@bot.on_command('yt')
@loading_status
def handle_yt(command: Command):
    '''
    `!yt <QUERY>` - Returns the top video search result based on the query string.
    '''
    if not command.has_arg():
        raise UsageSyntaxException()

    search_query = command.arg.strip()
    try:
        video_id = get_top_video_result(search_query, command.channel_id)
    except HttpError as e:
        bot.logger.error(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
        return

    if video_id is None:
        message = "Your query returned no results."
    else:
        message = f'{YOUTUBE_VIDEO_URL}{video_id}'
    bot.post_message(command.channel_id, message)
