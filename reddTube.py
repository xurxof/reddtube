import sys
import time

import gdata.youtube.service


def get_first(iterable, default=None):
    """
    returns the first item of iterable
    """
    if iterable:
        for item in iterable:
            return item
    return default


def getplaylist(yt_service, playlist_name):
    """
    yt_service:  YouTube service
    playlist: name to search
    Retruns the playlist object or None
    """
    playlist_feed = yt_service.GetYouTubePlaylistFeed(username='default')
    entries = [entry for entry in playlist_feed.entry if entry.title.text == playlist_name]
    return get_first(entries)


def create_playlist(yt_service, playlist_name, playlist_description, playlist_public):
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


def clear_playlist(yt_service, playlist, playlist_description):
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
        video_id = video_entry.id.text.split('/')[-1]
        yt_service.DeletePlaylistVideoEntry('http://gdata.youtube.com/feeds/api/playlists/' + playlist_id, video_id)


def get_video_id_from_url(video_url):
    import urlparse

    if 'www.youtube.com' in video_url:
        parsed = urlparse.urlparse(video_url)
        video_v_parameters = urlparse.parse_qs(parsed.query)
        if 'v' not in video_v_parameters:
            # not a video link, perhaps a list link?
            video_id = None
        else:
            video_id = video_v_parameters['v'][0]
    if 'youtu.be' in video_url:
        video_id = video_url.split('/')[-1]
    return video_id


def add_video_playlist(yt_service, playlist, video_id):

    if not video_id:
        return
    try:
        playlist_id = playlist.id.text.split('/')[-1]
        playlist_uri = 'http://gdata.youtube.com/feeds/api/playlists/' + playlist_id
        yt_service.AddPlaylistVideoEntryToPlaylist(playlist_uri, video_id)
    except gdata.service.RequestError as inst:
        response = inst[0]
        status = response['status']
        reason = response['reason']
        body = response['body']
        print "Request error. Status: {1} Reason:{2} Body: {3}".format(response, status, reason, body)


def get_all_youtube_url(url_origin):
    links = []
    # get youtube links from origin url
    from BeautifulSoup import BeautifulSoup
    import urllib2

    attempts = 0
    done = False
    while attempts < 5 and not done:
        try:
            html_page = urllib2.urlopen(url_origin)
        except urllib2.HTTPError as inst:
            print "HTTPError. Attemps: {0} Error: {1}".format(attempts, inst)
            attempts += 1
            time.sleep(10)
        else:
            print "Analyzing {0}".format(url_origin)
            soup = BeautifulSoup(html_page)
            for soup_link in soup.findAll('a'):
                link = soup_link.get('href')
                if link is None:
                    continue
                if ('www.youtube.com' in link or 'youtu.be' in link) and 'domain/youtu.be' not in link:
                    # TODO: best check
                    links.append(link)
            done = True
    video_ids=list(set([get_video_id_from_url(url) for url in links]))
    return video_ids



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


video_ids = get_all_youtube_url(url_origin)
if not video_ids:
    sys.exit('No video links founded. Playlist not updated')

# unique video ids

# read user playlists
playlist = getplaylist(yt_service, playlist_name)
if not playlist:
    playlist = create_playlist(yt_service, playlist_name, playlist_description, playlist_public)
else:
    clear_playlist(yt_service, playlist, playlist_description)

for video_id in video_ids:
    time.sleep(3)  # flood control
    print 'adding ' + video_id
    add_video_playlist(yt_service, playlist, video_id)


