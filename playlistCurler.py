#!/usr/bin/python
import argparse
import Queue
import sys
import os
from apiclient.discovery import build
from apiclient.errors import HttpError
from urlparse import urlparse, parse_qs

import default_config as config
from resources import *

def getYouTubeAPIHandler():
    """Get the YouTube API handler.
    """
    handler = build(config.YOUTUBE_API_SERVICE_NAME, config.YOUTUBE_API_VERSION,
                    developerKey=config.DEVELOPER_KEY)

    return handler

def addVideosToQueue(APIHandler, playlistId, dryrun, queue):
    """Add viedos info that we are going to download into a queue.

    Args:
        APIHandler - A YouTube API handler.
        playlistId - A playlist Id.
        dryrun - A boolean to tell if the current execution is dryrun or actual run.
        queue - A Queue created to store all the video info.
    """
    apiResponse = APIHandler.playlistItems().list(
            playlistId=playlistId,
            part='snippet',
            fields='items/snippet(resourceId/videoId,thumbnails/default/url,' \
                    'channelId,title)',
            maxResults=50
        ).execute()

    for video in apiResponse['items']:
        snippet = video['snippet']
        title = snippet['title'] if 'title' in snippet else None
        videoId = snippet['resourceId']['videoId']

        if dryrun:
            channelId = snippet['channelId'] if 'channelId' in snippet else None
            thumbnailsURL = snippet['thumbnails']['default']['url'] \
                            if 'thumbnails' in snippet else None
            message = """
            Title: %s
            ChannelId: %s
            VideoId: %s
            Thumbnail: %s
            """ % (title, channelId, videoId, thumbnailsURL)
            print message
            
        queue.put({'videoId': videoId, 'title': title})

def getPlayListTitle(APIHandler, playlistId):
    """Get the playlist's title.

    Args:
        APIHandler - A YouTube API handler.
        playlistId - A playlist Id.

    Returns:
        A playlist title.
    """
    apiResponse = APIHandler.playlists().list(
            id=playlistId,
            part='snippet',
            fields='items/snippet(title)'
        ).execute()

    # A playlist is gauranteed to have a title, according to YouTube.
    return apiResponse['items'][0]['snippet']['title']

def retrievePlaylistId(url):
    """Parse the url and get the play list Id.

    Args:
        url - The youtube url link.
    """
    parsed = urlparse(url)
    queryString = parse_qs(parsed.query)
    playlistId = queryString['list'][0] \
                if 'list' in queryString and queryString['list'] \
                else None

    return playlistId

def _checkDownloadLocation(destDir):
    """Check if the download location exists and if it is writable.
    """
    # This is to check if the destDir starts with '~'
    location = os.path.expanduser(destDir)
    if not os.path.isdir(location):
        raise Exception('Cannot find the destination directory. It does not exist. '
                        'Plese check the DOWNLOAD_LOCATION setting in '
                        'default_config, or use --location option with command line.')

    return location

def _getCommentLineArg():
    """Parse the commond line arguments.
    """
    parser = argparse.ArgumentParser(description='Download musics from YouTube ' 
                                                 'Playlist')
    parser.add_argument('--url', help='YouTube playlist URL', required=True)
    parser.add_argument('--location', help='Download directory', default=None)
    parser.add_argument('--execute', help='If passed, it will actually execute.',
                           dest='dryrun', action='store_false')

    return parser.parse_args()

def main():
    """Main loop to execute.
    """
    args = _getCommentLineArg()

    try:
        # If the location has been supplied in the command line, it overrides the
        # location in the default_config.
        location = _checkDownloadLocation(config.DOWNLOAD_LOCATION) \
                   if not args.location else _checkDownloadLocation(args.location)

        # Get YouTube API handler.
        APIHandler = getYouTubeAPIHandler()

        playlistId = retrievePlaylistId(args.url)
        if playlistId:
            # Retrieve playlist title.
            playlistTitle = getPlayListTitle(APIHandler, playlistId)

            # Create an infinite request queue, and start querying all the videos.
            requestQueue = Queue.Queue(0)
            addVideosToQueue(APIHandler, playlistId, args.dryrun, requestQueue)

            # Create download workers.
            for i in range(config.DOWNLOAD_WORKER_NUMBER):
                t = downloadWorker(requestQueue, playlistTitle, location,
                                   args.dryrun)
                t.daemon = True
                t.start()
            
            # Block the current thread until all tasks have been completed by
            # the workers.
            requestQueue.join()
        else:
            print 'Invalid url %s\n' % args.url
            return -1
    except HttpError, e:
        print 'An HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
        return -1
    except Exception as e:
        print e
        return -1

    return 0


if __name__ == '__main__':
    sys.exit(main())