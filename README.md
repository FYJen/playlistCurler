#Playlist Curler
Playlist Curler is a Python applicatioin that is capable of downloading songs from a given public YouTube playlist.

##Installation
The installation is really simple.
Just run, `pip install -r requirements.txt`

##Configuration
The only configuration place is in [default_config.py](./default_config.py/). You can set `DOWNLOAD_LOCATION` to any location you desire.

##Usage
Simply run, `python playlistCurler.py --url 'YOUTUBE_URL'`

Example:
	
	`python playlistCurler.py --url 'https://www.youtube.com/watch?v=lEKOWKcUxdU&list=PL9tY0BWXOZFtkcURIg7hkpWbpCBHCD5-G'`

`Note`: The YouTube URL needs to have `list='PLAYLIST_ID'` in the query string.

##How It Works
Playlist Curler uses [YouTube Data API V3](https://developers.google.com/youtube/v3/) to retrieve every individual song's information from a given public YouTube playlist. The retrieved song information contains `Id`, `title`, `thumbnail` and `channelId`. 

Once we get the song information, the Playlist Curler constructs two different URLs for individual song: one is used to retrieve unique hash for the song from [Youtube-mp3](http://www.youtube-mp3.org/), and the other is used to download the song.

- Hash retrieving URL format:
	* 'http://www.youtube-mp3.org/a/itemInfo/?video_id=%s&ac=www&t=grp&r=%s'
	* First `%s`: video/song `Id`
	* Second `%s`: timestamp in millisecond
- Download URL format:
	* 'http://www.youtube-mp3.org/get?ab=128&video_id=%s&h=%s&r=%s.%s'
	* First `%s`: video/song `Id`
	* Second `%s`: hash retrieved from the first URL
	* Third `%s`: timestamp in millisecond
	* Fourth `%s`: some suffix generated with algorithm

The hash retrieving URL can be obtained from inspecting `Network` tab of Chrome's Developer Tool.

The suffix generation funtion can be found in [resources/downloadWorker.py](https://github.com/FYJen/playlistCurler/blob/master/resources/downloadWorker.py#L49). The function is retrieved from inspecting youtube-mp3.org's client side JavaScript file.

`NOTE`: This application heavily relies on youtube-mp3's services. If youtube-mp3 decided to stop its service, this application might actually die XD.