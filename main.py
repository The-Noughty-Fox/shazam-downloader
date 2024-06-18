# This project is sponsored by DJ Fuzuli.
# - SoundCloud: https://soundcloud.com/djfuzuli
# - MixCloud: https://www.mixcloud.com/DJFuzuli/

import asyncio
import sys
import os

from shazamio import Shazam, Serialize

import pandas as pd
from yt_dlp import YoutubeDL
import youtube_search

AUDIO_EXTENSION = 'mp3'

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
  ydl_opts = {
    'overwrites': False,
    'outtmpl': 'shazamlibrary/%(title)s.%(ext)s',
    'format': 'mp3/bestaudio/best',
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': AUDIO_EXTENSION,
    }]
  }
  with YoutubeDL(ydl_opts) as ydl:
    for track_id in track_ids:
      try:
        print(f"Shazam: Reading track information for id {track_id}")
        about_track = await shazam.track_about(track_id=track_id)
        serialized = Serialize.track(data=about_track)
        (title, id) = yt_search(serialized.title + " - " + serialized.subtitle)
        url = f"https://www.youtube.com/watch?v={id}"
        print(f"YouTube: Downloading '{title}'")
        ydl.download([url])
      except Exception as e:
        print(e)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


