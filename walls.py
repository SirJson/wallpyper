#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import praw
import sys
import requests
from pathlib import Path
import random
from pprint import pformat
import subprocess
import socket
from configparser import ConfigParser
import reddit
from errors import ServerError, WallpaperStale
import json

supported_desktops = ['feh', 'dlonly', 'gnome', 'mate']


COOKIE = Path().home() / Path('.paper-cookie')
TEMP_PIC_PATH = Path().home() / Path('Pictures/wallpaper.jpg')
WALLPAPER_KEY = 'picture-uri'


def internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False


def reddit_wallpaper(client, secret, subreddits, last_id):
    wallpaper = None
    while wallpaper is None:
        try:
            wallpaper = reddit.get_random_submission(
                client_id=client, client_secret=secret, subreddits=subreddits, last_id=last_id)
        except WallpaperStale:
            print("Wallpaper seen before...")
        except ServerError:
            print("...")

    url = wallpaper.preview['images'][0]['source']['url']
    response = requests.get(url)

    if response.status_code != requests.codes['ok']:
        sys.exit(2)

    with open(str(COOKIE), 'w') as cookie_file:
        cookie_file.write(wallpaper.id)

    with open(str(TEMP_PIC_PATH), 'wb') as pic:
        pic.write(response.content)


def get_feh():
    output = Path('/usr/bin/feh')
    if not output.exists():
        output = Path('/usr/local/bin/feh')  # User compliled FEH
    return output


def set_gnome_wallpaper(path: str):
    # We local import because we often don't need Gtk or Gio
    from gi.repository import Gio
    conf_schema = 'org.gnome.desktop.background'
    conf_key = 'picture-uri'
    settings = Gio.Settings.new(conf_schema)
    settings.set_string(conf_key, f'file://{path}')


def main():
    config = ConfigParser()
    config.read(Path.home() / ".config" / "wallpyper.conf")
    desktop = config['Desktop']['type']

    last_id = None
    if COOKIE.exists():
        with open(COOKIE) as cookie:
            last_id = cookie.read()

    if internet():
        reddit_wallpaper(config['Reddit']['client'], config['Reddit']
                         ['secret'], config['Reddit']['subreddits'].split(','), last_id)
    else:
        sys.exit(4)

    if desktop == 'feh':
        subprocess.run([str(get_feh()), '--bg-scale', str(TEMP_PIC_PATH)])
    elif desktop == 'gnome':
        set_gnome_wallpaper(str(TEMP_PIC_PATH))
    elif desktop == 'mate':
        subprocess.Popen(["gsettings", "set", "org.mate.background",
                          "picture-filename", f"'{str(TEMP_PIC_PATH)}'"])
    else:
        sys.exit(-1)


main()
