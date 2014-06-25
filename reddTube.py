import gdata.youtube.service
import sys

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
		

playlist_name = sys.argv[1]
playlist_description = playlist_name
playlist_public = True

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


playlist= getplaylist (yt_service, playlist_name)
if not playlist:
	playlist = create_playlist (yt_service, playlist_name, playlist_description, playlist_public)
else:
	clear_playlist (yt_service, playlist, playlist_description)
