# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = 'AIzaSyBxa6WbBaQYJT6VBu0NKpGsD7e2qr_Ot-0'  # Apr 30, 2014 9:00 PM
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Default youtube video URL.
YOUTUBE_VIDEO_URL = 'www.youtube.com/watch?v=%s'

# Third party service that we will post our requests to.
CUSTOM_HEADER = {'Accept-Location': '*'}
YOUTUBE_TO_MP3_VIDEO_HASH = 'http://www.youtube-mp3.org/a/itemInfo/?video_id=%s&ac=www&t=grp&r=%s'
YOUTUBE_TO_MP3_VIDEO_DOWNLOAD = 'http://www.youtube-mp3.org/get?ab=128&video_id=%s&h=%s&r=%s.%s'

# Number of download workers.
DOWNLOAD_WORKER_NUMBER = 3
