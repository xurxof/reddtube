import gdata.youtube.service
import time
from utils import attempts


def get_first(iterable, default=None):
    """
    returns the first item of iterable
    """
    if iterable:
        for item in iterable:
            return item
    return default


def create_playlist(yt_service, playlist_name, playlist_description, private=True):
    """
    yt_service:  YouTube service
    playlist_name: name for the playlist
    playlist_description: description for the playlist
    playlist_public: true for create a public playlist
    Returns the playlist
    """

    new_playlist_entry = yt_service.AddPlaylist(playlist_name, playlist_description, private)

    if isinstance(new_playlist_entry, gdata.youtube.YouTubePlaylistEntry):
        return new_playlist_entry
    else:
        return None


def get_playlist(yt_service, playlist_name):
    """
    yt_service:  YouTube service
    playlist: name to search
    Returns the playlist object or None
    """
    playlist_feed = yt_service.GetYouTubePlaylistFeed(username='default')
    entries = [entry for entry in playlist_feed.entry if entry.title.text == playlist_name]
    return get_first(entries)


def clear_playlist(yt_service, playlist, playlist_description):
    """
    playlist:  YouTubePlaylistEntry object representing playlist to clear
    playlist_description: new description for the playlist
    Public/private attribute not change
    """
    # playlist.id.text is something like http://gdata.youtube.com/feeds/api/users/bQQl1gQ/playlists/PLyhw-VhRP-i3AwJBx
    playlist_id = playlist.id.text.split('/')[-1]
    original_title = playlist.title.text

    yt_service.UpdatePlaylist(playlist_id, original_title, playlist_description)

    playlist_video_feed = yt_service.GetYouTubePlaylistVideoFeed(playlist_id=playlist_id)

    for video_entry in playlist_video_feed.entry:
        video_id = video_entry.id.text.split('/')[-1]
        yt_service.DeletePlaylistVideoEntry('http://gdata.youtube.com/feeds/api/playlists/' + playlist_id, video_id)


def login(username, password, developer_key):
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.email = username
    yt_service.password = password
    yt_service.source = 'reddTube'
    yt_service.developer_key = developer_key
    yt_service.client_id = 'reddTube'
    yt_service.ProgrammaticLogin()
    return yt_service


def add_video_playlist(yt_service, playlist, video_id, max_attempts):
    def request_err_description(inst):
        """
        inst: request exception
        """
        response = inst[0]
        status = response['status']
        reason = response['reason']
        body = response['body']
        return status, "Request error. Status: {1} Reason:{2} Body: {3}".format(response, status, reason, body)

    if not video_id:
        return
    attempts = 0

    while attempts < max_attempts:
        try:
            playlist_id = playlist.id.text.split('/')[-1]
            playlist_uri = 'http://gdata.youtube.com/feeds/api/playlists/' + playlist_id
            yt_service.AddPlaylistVideoEntryToPlaylist(playlist_uri, video_id)
            break
        except gdata.service.RequestError as inst:
            status, description = request_err_description(inst)
            attempts += 1
            # status codes: 403 - forbidden; 400 - bad request body; 404 - not found;
            if attempts == max_attempts or status in [403, 400, 404]:
                return request_err_description(inst)
                break
            time.sleep(5)