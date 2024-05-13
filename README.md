# OvercastPodcastAutoFetch

**TL;DR:** I created OvercastPodcastAutoFetch to download the audio files of podcasts I listen to in Overcast on my mac. Complementing this, I developed another script called [AutoWhisperWatcher](https://github.com/danielraffel/AutoWhisperWatcher/) to transcribe those files locally using [MacWhisper](https://goodsnooze.gumroad.com/l/macwhisper).

OvercastPodcastAutoFetch is designed to automatically monitor an RSS feed provided by the [Overcast podcast activity feed](https://github.com/dblume/overcast-podcast-activity-feed). This script identifies new podcast episodes that I've listened to in Overcast, downloads them to a specified folder on macOS, and is designed to work with [AutoWhisperWatcher](https://github.com/danielraffel/AutoWhisperWatcher/) for automated transcription via [MacWhisper](https://goodsnooze.gumroad.com/l/macwhisper). This integration ensures a streamlined process from downloading to transcription. The tool also incorporates a mechanism to prevent re-downloading episodes by maintaining a history of what has been downloaded, ensuring efficient use of storage and network resources.

## Installation

### Prerequisites

- **Homebrew**: Ensure that Homebrew is installed on your system. If not, install it by running:
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- **Python 3**: Make sure Python 3 is installed. If not, install it using Homebrew:
  ```bash
  brew install python3
  ```
- **GNU Screen**: If not already installed, use Homebrew to install it:
  ```bash
  brew install screen
  ```

### Step 1: Clone the Repository

Clone the OvercastPodcastAutoFetch repository to your local machine:
```bash
git clone https://github.com/danielraffel/OvercastPodcastAutoFetch.git
cd OvercastPodcastAutoFetch
```

### Step 2: Install Python Dependencies

Install the required Python libraries:
```bash
pip3 install feedparser requests
```

## Setup

### Step 1: Configuration

Create a configuration file named `config.py` and fill in the necessary details:
```python
# config.py
FEED_URL = "https://yousite.com/podcast_activity.xml"
DOWNLOAD_FOLDER = "$HOME/podcastaudio/"
HISTORY_FILE = "$HOME/podcast_history.txt"
```

### Step 2: Create the Fetch Script

Create a Python script named `fetch_podcasts.py` that will monitor the RSS feed, download new files, and record their identifiers:
```python
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
```
Save this script in your cloned repository.

### Step 3: Make the Script Executable

```bash
chmod +x fetch_podcasts.py
```

## Usage

### Starting the Fetch Script

To start fetching in a screen session:

```bash
screen -S OvercastPodcastAutoFetch
./fetch_podcasts.py
```
Detach from the screen session by pressing `CTRL+A` followed by `D`.

### Stopping the Fetch Script

To stop the script:

- Reattach to the screen session:
  ```bash
  screen -r OvercastPodcastAutoFetch
  ```
- Terminate the script by pressing `CTRL+C`.
- Exit the screen session:
  ```bash
  exit
  ```

## Automation

### Configure to Run at Startup

Open crontab editor:
```bash
crontab -e
```
Add the following line to run the script at reboot (update the path if your monitoring script is not in your Home directory):
```bash
@reboot screen -dmS OvercastPodcastAutoFetch /path/to/fetch_podcasts.py
```

## Conclusion

OvercastPodcastAutoFetch provides an automated solution to monitor an RSS feed, download new podcast files to a specified directory, and ensure no file is downloaded more than once by tracking downloaded episodes in a history file.
