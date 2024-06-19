# This project is sponsored by DJ Fuzuli.
# - SoundCloud: https://soundcloud.com/djfuzuli
# - MixCloud: https://www.mixcloud.com/DJFuzuli/

import asyncio
import sys
import os
import traceback

from shazamio import Shazam, Serialize

import pandas as pd
from yt_dlp import YoutubeDL
import youtube_search

AUDIO_EXTENSION = 'mp3'
YDL_OPTS = {
  'overwrites': False,
  'format': 'mp3/bestaudio/best',
  'postprocessors': [{  # Extract audio using ffmpeg
      'key': 'FFmpegExtractAudio',
      'preferredcodec': AUDIO_EXTENSION,
  }]
}
ERROR_LOG_FILE = "error_logs.txt"

def read_shazam_track_ids():
  # Read the CSV file
  file_path = sys.argv[1]
  df = pd.read_csv(file_path, skiprows=1)
  
  # Extract the Track IDs
  return df['TrackKey'].unique().tolist()

def yt_search(name):
  with youtube_search.YoutubeSearch() as ytsearch:
    print(f"YouTube: Searching for '{name}'")
    ytsearch.search(name)
    result = ytsearch.list()[0]

  return (result['title'], result['id'])

async def main():
  track_ids = read_shazam_track_ids()
  shazam = Shazam()
  if os.path.exists(ERROR_LOG_FILE):
    os.remove(ERROR_LOG_FILE)
  for track_id in track_ids:
    try:
      print(f"Shazam: Reading track information for id {track_id}")
      about_track = await shazam.track_about(track_id=track_id)
      serialized = Serialize.track(data=about_track)
      title = serialized.title + " - " + serialized.subtitle

      song_section = next(section for section in serialized.sections if section.type == 'SONG')
      if song_section:
        label = next(m.text for m in song_section.metadata if m.title == 'Label')
      (yt_title, id) = yt_search(title)
      full_title = title if not label else f"{title} [{label}]"

      url = f"https://www.youtube.com/watch?v={id}"
      print(f"YouTube: Downloading '{title}'")
      opts = YDL_OPTS.copy()
      opts['outtmpl'] = f"shazamlibrary/{full_title}.%(ext)s"
      with YoutubeDL(opts) as ydl:
        ydl.download([url])
    except Exception as e:
      logf = open(ERROR_LOG_FILE, "a")
      logf.write(f"{traceback.format_exc()}\n")
      logf.close()
      print(e)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


