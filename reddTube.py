from datetime import datetime
import sys
import time

import youtube


def get_playlist_description(original_title, original_url):
    message = '{0}, an automatic playlist created with the links of {1}. Last update: {2}'
    return message.format(original_title, original_url, datetime.today().strftime("%X %x"))


def get_video_id_from_url(video_url):
    import urlparse

    if 'www.youtube.com' in video_url or 'feature=youtu.be' in video_url:
        parsed = urlparse.urlparse(video_url)
        video_v_parameters = urlparse.parse_qs(parsed.query)
        if 'v' not in video_v_parameters:
            # not a video link, perhaps a list link?
            video_id = None
        else:
            video_id = video_v_parameters['v'][0]
    elif 'youtu.be' in video_url:
        video_id = video_url.split('/')[-1]
    return video_id


def get_all_youtube_url(url_origin):
    links = []
    # get youtube links from origin url
    from BeautifulSoup import BeautifulSoup
    import urllib2
    max_attempts = 5
    attempts = 0
    html_page=None

    while attempts < max_attempts:
        try:
            html_page = urllib2.urlopen(url_origin)
            break
        except urllib2.HTTPError as inst:
            print "HTTPError. Attempts: {0} Error: {1}".format(attempts, inst)
            attempts += 1
            time.sleep(4)
    if not html_page:
        return []

    print "Analyzing {0}".format(url_origin)
    soup = BeautifulSoup(html_page)
    for soup_link in soup.findAll('a'):
        link = soup_link.get('href')
        if link is None:
            continue
        if 'domain/youtu.be' in link:
            continue
        if 'www.youtube.com' in link or 'youtu.be' in link:
            # TODO: best check
            links.append(link)

    return list(set([get_video_id_from_url(url) for url in links]))

def read_config():

    with open('password.hide') as f:
        username, password = f.readline().strip().split(':')
        developer_key = f.readline().strip()
    cfg_playlists = [map(str.strip,line.split('|')) for line in open('playlists.cfg')]
    return username, password, developer_key, cfg_playlists


username, password ,developer_key, cfg_playlists = read_config()

yt_service=youtube.login(username, password, developer_key)
print 'Logged'

for cfg_playlist in cfg_playlists:
    playlist_name, url_origin = cfg_playlist[0:2]
    print 'Updating {0} with {1}'.format(playlist_name, url_origin)

    # unique video ids
    video_ids = get_all_youtube_url(url_origin)
    if not video_ids:
        sys.exit('No video links founded. Playlist not updated')

    # read user play lists
    playlist = youtube.get_playlist(yt_service, playlist_name)
    playlist_description = get_playlist_description(playlist_name, url_origin)

    if not playlist:
        playlist = youtube.create_playlist(yt_service, playlist_name, playlist_description)
    else:
        youtube.clear_playlist(yt_service, playlist, playlist_description)

    for video_id in video_ids:
        print 'adding ' + video_id
        youtube.add_video_playlist(yt_service, playlist, video_id, max_attempts=5)


