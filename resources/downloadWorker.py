#!/usr/bin/python
import json
import requests
import threading
import time
import os

import default_config as config

WORKER_MOD_NUMBER = 3

class downloadWorker(threading.Thread):
    """downloadWorker class which will contruct a queue
    """
    def __init__(self, queue, playlistTitle, location, dryrun):
        super(downloadWorker, self).__init__()
        self.queue = queue
        self.playlistTitle = playlistTitle.strip().replace(' ', '_')
        self.dryrun = dryrun
        self.location = os.path.join(location, self.playlistTitle)

    def __getVideoHash(self, curTime, videoId):
        """Retrieve a video hash for download URL. Required by youtube-to-mp3's api.

        Args:
            curTime - A string time in ms.
            videoId - A YouTube video Id.

        Returns:
            video hash or None.
        """
        videoHash = None
        url = config.YOUTUBE_TO_MP3_VIDEO_HASH % (videoId, curTime)
        response = requests.get(url, headers=config.CUSTOM_HEADER)

        if response.status_code == 200 and response.content:
            # Returned value of response.content will be a string of info.
            #       'info = {'title' : 'blah', ...... };'
            # We splite the first occurance of '=', then grab the second item in the
            # array. Remove the ';' at the end, and then strip away the whitespace
            # at the beginning of the dictionary. After that, we load it to json
            # structure.
            data = json.loads(response.content.split('=', 1)[-1][:-1].strip())
            if data['status'] == 'serving':
                videoHash = data['h']

        return videoHash

    def __generateSuffix(self, curTime, videoId):
        """Generate a suffix for download URL. Required by youtube-to-mp3's api.

        Args:
            curTime - A string time in ms.
            videoId - A YouTube video Id.

        Returns:
            A formulated suffix.
        """
        dataString = videoId + curTime
        AM = 65521
        b = 1
        c = 0
        for i in dataString:
            b = (b + ord(i)) % AM
            c = (c + b) % AM

        return c << 16 | b

    def __createPlayListTitleDir(self):
        """Create final dest directory if it doesn't exist.
        """
        try:
            os.makedirs(self.location)
        except OSError as e:
            print u'Directory exists: %s. Skip creating the directory.' % \
                  self.location

    def _constructURL(self, videoId):
        """Construct a download URL.

        Args:
            curTime - A string time in ms.
            videoId - A YouTube video Id.

        Returns:
            A download url.
        """
        curTime = str(int(time.time()))
        videoHash = self.__getVideoHash(curTime, videoId)
        if videoHash is None:
            raise Exception('Cannot extract hash for the video, %s.' % videoId)

        suffix = self.__generateSuffix(curTime, videoId)

        return config.YOUTUBE_TO_MP3_VIDEO_DOWNLOAD % (videoId, videoHash, curTime,
                                                       suffix)

    def _download(self, item):
        """Download musics.

        Args:
            item - Item from the Queue.
        """
        try:
            url = self._constructURL(item['videoId'])
            dest =  os.path.join(self.location, '%s.mp3' % item['title'])

            s = requests.Session()
            s.headers.update(config.CUSTOM_HEADER)
            r = s.get(url, stream=True)
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
        except Exception as e:
            print e

    def run(self):
        """Override thread's run method.
        """
        if self.dryrun:
            while True:
                item = self.queue.get()
                print self._constructURL(item['videoId'])
                self.queue.task_done()
        else:
            self.__createPlayListTitleDir()
            while True:
                item = self.queue.get()
                self._download(item)
                self.queue.task_done()