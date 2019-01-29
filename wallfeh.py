#!/usr/bin/env python3

import socket
import os
import subprocess
import praw
import logging
import re
from platform import platform
from dotenv import load_dotenv
from pathlib import Path
from util import Net

# feh --bg-fill %url


def loaded_wallpaper() -> str:
    loader = Path.home() / '.fehbg'
    if not loader.exists():
        return ''
    with open(loader) as script:
        result = re.search("'(.*)'", script.read(), re.M)
        return result.group(1)


def main():
    try:
        load_dotenv(verbose=True)
        logging.basicConfig(filename='/tmp/wallfeh.log',
                            filemode='w', level=logging.DEBUG)
        agent = f'{platform()}:wallfeh.py:v0.0.1 (by /u/SirJson)'
        logging.debug(agent)

        logging.info("Testing connection...")
        Net.TestConnection().unwrap()

        reddit = praw.Reddit(client_id=os.environ['WALLFEH_REDDIT_ID'],
                             client_secret=os.environ['WALLFEH_REDDIT_SECRET'], user_agent=agent)
        current = loaded_wallpaper()
        logging.info(f'Current wallpaper source: {current}')
        logging.info(f'Fetching wallpaper urls')
        url_list = list(map(lambda y: y.preview['images'][0]['source']['url'],
                            filter(lambda x: x.thumbnail is 'self', reddit.multireddit(
                                os.environ['WALLFEH_SUBREDDITS']).hot())))

        print(submission.title)
    except Exception ex:
        logging.error(f'Crash: {ex}')


main()
