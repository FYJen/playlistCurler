#!/usr/bin/python
import argparse
import Queue
import sys
from apiclient.discovery import build
from apiclient.errors import HttpError
from urlparse import urlparse, parse_qs

import default_config as config
from resources import *

def addVideosToQueue(playListId, dryrun, queue):
    """
    """
    youtubeAPI = build(config.YOUTUBE_API_SERVICE_NAME, config.YOUTUBE_API_VERSION,
                       developerKey=config.DEVELOPER_KEY)

    apiResponse = youtubeAPI.playlistItems().list(
            playlistId = playListId,
            part = 'snippet',
            fields = 'items/snippet(resourceId/videoId,thumbnails/default/url,' \
                     'channelId,title)',
            maxResults = 50
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

def retrievePlaylistId(url):
    """Parse the url and get the play list Id.

    Args:
        url - The youtube url link.
    """
    parsed = urlparse(url)
    queryString = parse_qs(parsed.query)
    playListId = queryString['list'][0] \
                if 'list' in queryString and queryString['list'] \
                else None

    return playListId 

def _getCommentLineArg():
    """Parse the commond line arguments.
    """
    parser = argparse.ArgumentParser(description='Download musics from YouTube ' 
                                                 'Playlist')
    parser.add_argument('--url', help='YouTube playlist URL', required=True)
    parser.add_argument('--location', help='Download directory', required=True)
    parser.add_argument('--execute', help='If passed, it will actually execute.',
                           dest='dryrun', action='store_false')

    return parser.parse_args()

def main():
    """
    """
    args = _getCommentLineArg()

    try:
        playListId = retrievePlaylistId(args.url)
        if playListId:
            # create an infinite request queue
            requestQueue = Queue.Queue(0)

            # start querying all the videos and add them to request queue
            addVideosToQueue(playListId, args.dryrun, requestQueue)

            # create download workers
            for i in range(config.DOWNLOAD_WORKER_NUMBER):
                t = downloadWorker(requestQueue, args.location, args.dryrun)
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

    return 0


if __name__ == '__main__':
    sys.exit(main())