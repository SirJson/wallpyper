#!/usr/bin/pyedge
# -*- coding: utf-8 -*-

import praw
import sys
import requests
from pathlib import Path
import argparse
import random
from pprint import pformat
import subprocess
import socket

supported_desktops = ['feh', 'dlonly', 'gnome', 'mate']

parser = argparse.ArgumentParser()
parser.add_argument("desktop")
args = parser.parse_args()

if args.desktop not in supported_desktops:
    print('Unknown desktop enviroment: ' + args.desktop)
    sys.exit(2)

USER_AGENT = 'linux:hot_wallpaper:v1.4 (by /u/SirJson)'
FEH_PATH = Path('/usr/bin/feh')
if not FEH_PATH.exists():
    FEH_PATH = Path('/usr/local/bin/feh')  # User compliled FEH
CLIENT_ID = '9A1OaCeg__yFtQ'
COOKIE = Path().home() / Path('.paper-cookie')
TEMP_PIC_PATH = Path().home() / Path('Pictures/wallpaper.jpg')
WALLPAPER_KEY = 'picture-uri'
SUBREDDITS = ['wallpaper', 'WQHD_Wallpaper', 'wallpapers', 'MinimalWallpaper',
              'ExposurePorn',]

last_id = ''

if COOKIE.exists():
    with open(str(COOKIE), 'r') as cookie_file:
        last_id = cookie_file.read()


def internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False


def get_random_submission():
    reddit = praw.Reddit(
        client_id=CLIENT_ID, client_secret='Gh07f3i0D5W2Wkrc4s8PqKbQWOo', user_agent=USER_AGENT)
    subreddit_name = random.choice(SUBREDDITS)
    print('Using subreddit: ' + subreddit_name)
    submission = None
    submissions = reddit.subreddit(subreddit_name).hot(limit=10)

    for item in submissions:
        if item.thumbnail != 'self':
            submission = item
            break

    if submission is None:
        print('Something went wrong. There is no submission for this post')
        sys.exit(3)

    current_id = submission.id

    print('Current id = ' + current_id)

    if last_id == current_id:
        print('No new wallpaper')
        return None

    return submission


def download_wallpaper():
    wallpaper = get_random_submission()
    while wallpaper is None:
        wallpaper = get_random_submission()

    print('Downloading new wallpaper...')
    url = wallpaper.preview['images'][0]['source']['url']
    response = requests.get(url)

    if response.status_code != requests.codes['ok']:
        print("Download failed!")
        sys.exit(2)

    with open(str(COOKIE), 'w') as cookie_file:
        cookie_file.write(wallpaper.id)

    with open(str(TEMP_PIC_PATH), 'wb') as pic:
        pic.write(response.content)


def set_gnome_wallpaper(path: str):
    # We local import because we often don't need Gtk or Gio
    from gi.repository import Gio
    conf_schema = 'org.gnome.desktop.background'
    conf_key = 'picture-uri'
    settings = Gio.Settings.new(conf_schema)
    settings.set_string(conf_key, f'file://{path}')


if internet():
    print("We are online!")
    download_wallpaper()
else:
    print("Can not update wallpaper. There seems to be no internet connection.")
    sys.exit(0)

if args.desktop == 'feh':
    subprocess.run([str(FEH_PATH), '--bg-scale', str(TEMP_PIC_PATH)])
elif args.desktop == 'gnome':
    set_gnome_wallpaper(str(TEMP_PIC_PATH))
elif args.desktop == 'mate':
    subprocess.Popen(["gsettings", "set", "org.mate.background",
                      "picture-filename", f"'{str(TEMP_PIC_PATH)}'"])
