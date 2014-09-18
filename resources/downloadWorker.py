#!/usr/bin/python

import requests
import threading

import default_config as config

WORKER_MOD_NUMBER = 3

class downloadWorker(threading.Thread):
    """downloadWorker class which will contruct a queue
    """
    def __init__(self, queue, location, dryrun):
        super(downloadWorker, self).__init__()
        self.queue = queue
        self.dryrun = dryrun
        self.location = location

    def __constructURL(self, videoId):
        """
        """
        youtubeURL = config.YOUTUBE_VIDEO_URL % videoId
        return config.YOUTUBEINMP3 % youtubeURL

    def __download(self, item):
        """
        """
        url = self.__constructURL(item['videoId'])
        if self.location[-1] != '/':
            dest = self.location + '/' + item['title'] + '.mp3'
        else:
            dest = self.location + item['title'] + '.mp3'
        s = requests.Session()
        s.headers.update({'Accept-Location': '*'})
        r = s.get(url, stream=True)
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()

    def run(self):
        """
        """
        if self.dryrun:
            while True:
                item = self.queue.get()
                print self.__constructURL(item['videoId'])
                self.queue.task_done()
        else:
            while True:
                item = self.queue.get()
                self.__download(item)
                self.queue.task_done()