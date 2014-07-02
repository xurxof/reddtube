import gdata.youtube.service
import sys
import time

def get_first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default


def getplaylist (yt_service, playlist_name):
	"""
	yt_service:  YouTube service
	playlist: name to search
	Retruns the playlist object or None
	"""
	playlist_feed = yt_service.GetYouTubePlaylistFeed(username='default')
	entries = [entry for entry in playlist_feed.entry if entry.title.text == playlist_name]
	return get_first(entries)

def create_playlist (yt_service, playlist_name, playlist_description, playlist_public):
	"""
	yt_service:  YouTube service
	playlist_name: name for the playlist
	playlist_description: description for the playlist
	playlist_public: true for create a public playlist
	Returns the playlist
	"""
	new_playlistentry = yt_service.AddPlaylist(playlist_name, playlist_description, playlist_public)

	if isinstance(new_playlistentry, gdata.youtube.YouTubePlaylistEntry):
		return new_playlistentry
	else:
		return None

def clear_playlist (yt_service, playlist, playlist_description):
	"""
	playlist:  YouTubePlaylistEntry object representing playlist to clear
	playlist_description: new description for the playlist
	Public/private attribute not change
	"""
	# playlist.id.text is something like http://gdata.youtube.com/feeds/api/users/bQQl1gQ/playlists/PLyhw-VhRP-i3AwJBx
	playlist_id = playlist.id.text.split('/')[-1]
	
	original_title = playlist.title.text
	# updated_playlist = yt_service.UpdatePlaylist(playlist_id,
	#	                                         original_title,
	#	                                         playlist_description)

	playlist_video_feed = yt_service.GetYouTubePlaylistVideoFeed(playlist_id=playlist_id)
	for video_entry in playlist_video_feed.entry:
		video_id= video_entry.id.text.split('/')[-1]
		yt_service.DeletePlaylistVideoEntry('http://gdata.youtube.com/feeds/api/playlists/' + playlist_id, video_id)
		
def add_video_playlist (yt_service, playlist, video_url):
	import urlparse
	try:
		if 'www.youtube.com' in video_url:
			parsed = urlparse.urlparse(video_url)
			video_v_parameters = urlparse.parse_qs(parsed.query)
			if 'v' not in video_v_parameters:
				# not a video link, perhaps a list link?
				return 
			video_id = video_v_parameters['v'][0]
		if 'youtu.be' in video_url:
			video_id = video_url.split('/')[-1]

		playlist_id = playlist.id.text.split('/')[-1]
		playlist_uri = 'http://gdata.youtube.com/feeds/api/playlists/' + playlist_id

		playlist_video_entry = yt_service.AddPlaylistVideoEntryToPlaylist(playlist_uri, video_id)
	except gdata.service.RequestError as inst:
		response = inst[0]  
		status = response['status']  
		reason = response['reason']  
		body = response['body']  
		print "Request error. Status: {1} Reason:{2} Body: {3}".format(response, status, reason, body )

playlist_name = sys.argv[1]
playlist_description = playlist_name
playlist_public = True
url_origin = sys.argv[2]


print 'Updating ' + playlist_name + ' with ' + url_origin

# Create a client class which will make HTTP requests with Google Docs server.
with open('password.hide') as f:
  username, password = f.readline().strip().split(':')
  developer_key = f.readline().strip()

yt_service = gdata.youtube.service.YouTubeService()
yt_service.email = username
yt_service.password = password
yt_service.source = 'reddTube'
yt_service.developer_key = developer_key
yt_service.client_id = 'reddTube'
yt_service.ProgrammaticLogin()
print 'Logged'

def get_all_youtube_url(url_origin):
	links=[]
	# get youtube links from origin url
	from BeautifulSoup import BeautifulSoup
	import urllib2
	import re
	attemps=0
	done=False
	while attemps<3 and not done:
		try:
			html_page = urllib2.urlopen(url_origin)
		except urllib2.HTTPError as inst:
			print "HTTPError. Attemps: {0} Error: {1}".format(attemps, inst)
			attemps	+=1
		else:	
			print "Analyzing {0}".format(url_origin)
			soup = BeautifulSoup(html_page)
			for soup_link in soup.findAll('a'):
				link = soup_link.get('href')
				if link is None:
					continue
				if ('www.youtube.com' in link or 'youtu.be' in link) and link not in links and 'domain/youtu.be' not in link:
					# TODO: best check
					links.append(link)
			done = True
	return links


youtube_videos_links=get_all_youtube_url(url_origin)
if not youtube_videos_links:
	sys.exit ('No video links founded. Playlist not updated')



# read user playlists
playlist= getplaylist (yt_service, playlist_name)
if not playlist:
	playlist = create_playlist (yt_service, playlist_name, playlist_description, playlist_public)
else:
	clear_playlist (yt_service, playlist, playlist_description)

for link in youtube_videos_links:
	time.sleep(3) # flood control
	print 'adding ' + link
	add_video_playlist (yt_service, playlist, link)


