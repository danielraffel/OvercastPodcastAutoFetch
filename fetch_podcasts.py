#!/usr/bin/env python3
import feedparser
import requests
import os
from urllib.parse import urlparse

# Load configuration
from config import FEED_URL, DOWNLOAD_FOLDER, HISTORY_FILE

def download_file(url, guid):
    local_filename = os.path.join(DOWNLOAD_FOLDER, os.path.basename(urlparse(url).path))
    if not os.path.exists(local_filename):
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        with open(HISTORY_FILE, 'a') as h:
            h.write(f"{guid}\n")
        return local_filename

def main():
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    downloaded_guids = set()
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as h:
            downloaded_guids.update(h.read().splitlines())

    feed = feedparser.parse(FEED_URL)
    for entry in feed.entries:
        guid = entry.get('id')
        enclosure_url = entry.enclosures[0]['href'] if entry.enclosures else None
        if enclosure_url and guid not in downloaded_guids:
            print(f"Downloading {enclosure_url}")
            download_file(enclosure_url, guid)

if __name__ == "__main__":
    main()
