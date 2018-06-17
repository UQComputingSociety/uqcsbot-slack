import os
from uqcsbot import bot, Command

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v='
NO_QUERY_MESSAGE = "You can't look for nothing. !yt <QUERY>"


@bot.on_command('yt')
def handle_yt(command: Command):
    '''
    `!yt <QUERY>` - Returns the top video search result based on the query string.
    '''
    # Makes sure the query is not empty.
    if not command.has_arg():
        bot.post_message(command.channel_id, NO_QUERY_MESSAGE)
        return

    search_query = command.arg.strip()
    try:
        videoID = get_top_video_result(search_query, command.channel_id)
    except HttpError as e:
        # Googleapiclient should handle http errors
        bot.logger.error(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
        # Force return to ensure no message is sent.
        return

    if videoID:
        bot.post_message(command.channel_id, f'{YOUTUBE_VIDEO_URL}{videoID}')
    else:
        bot.post_message(command.channel_id, "Your query returned no results.")


def get_top_video_result(search_query: str, channel):
    '''
    The normal method for using !yt searches based on query
    and returns the first video result. "I'm feeling lucky"
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
