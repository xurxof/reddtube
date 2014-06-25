import gdata.youtube.service
import sys





def getplaylist (playlist_feed, playlist_name):
	"""
	playlist_feed:  YouTubePlaylistEntry
	playlist: name to search
	"""
	entries = [entry for entry in playlist_feed.entry if entry.title.text == playlist_name]
	return entries


playlist_name = sys.argv[1]

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
print yt_service.ProgrammaticLogin()

# read user playlists
playlist_feed = yt_service.GetYouTubePlaylistFeed(username='default')

print getplaylist (playlist_feed, playlist_name)


