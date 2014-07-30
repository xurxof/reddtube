# _reddtube_

Create youtube playlists from any web page.

## Project Setup

Requirements:

    BeautifulSoup==3.2.1
    argparse==1.2.1
    gdata==2.0.18
    wsgiref==0.1.2


## Testing

Sorry, not test available :_(

## Deploying

1. A 'password.hide' file must contains your gmail user and password  and your youtube api key. password.hide.sample is provided as example.
2. The URLs and playlists names must be write down in a 'playlists.cfg'. A 'playlists.cfg.sample' is provided as example. Write each entry in a new line, and values must be separated by a pipe (|) char.

Example:

    ReddTube MusicForConcentration | http://www.reddit.com/r/MusicForConcentration
    ReddTube World Music  | http://www.reddit.com/r/WorldMusic

## Troubleshooting & Useful Tools

It is easy obtain a 429 HTTP 'Too many requests' exception from Reddit. The script try be gently and only retry http calls few times and after wait few seconds.
Continuous run or large playlist file can result in Google API exception due quota limits.

## ToDo

- Best gmail configuration (be careful: password stored in plain text!)
- Pass in argument the filename of playlists config

## License

MIT license
