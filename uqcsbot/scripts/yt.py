import os
from uqcsbot import bot, Command
import argparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

YOUTUBE_API_KEY = 'AIzaSyCtxVMs6So6x2WL5WkDV4rm01hzddCCGH4'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v='


@bot.on_command('yt')
def handle_yt(command: Command):
    '''
    `!yt <QUERY>` - Returns the top search result based on the query string.
    
    handle_yt checks the usage of yt command and appropriately selects logic.
    '''
    # Makes sure the query is not empty.
    if command.has_arg():
        try:
            cmd = command.arg.strip()
            yt_normal(cmd, command.channel)
        except HttpError as e:
            # Googleapiclient should handle http errors
            print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
    else:
        bot.post_message(command.channel, "You can't look for nothing. !yt <QUERY>")
        
def yt_normal(search_query: str, channel):
    '''
    The normal method for using !yt searches based on query
    and returns the first result. "I'm feeling lucky"
    '''
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=YOUTUBE_API_KEY)

    search_response = youtube.search().list(
        q=search_query,
        part='id', # Only the video ID is needed to get video link
        maxResults=1, # Since only one video is linked this is the only result we need
        type='video' # Only want videos no pesky channels or playlists
    ).execute()
    
    search_result = search_response.get('items',[])

    if len(search_result):
        videoId = search_result[0]['id']['videoId']
        message = YOUTUBE_VIDEO_URL+videoId
        bot.post_message(channel, message)
    else:
        bot.post_message(channel, "Your query returned no results.")