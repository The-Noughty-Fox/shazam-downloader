import asyncio
import sys

from shazamio import Shazam, Serialize

import pandas as pd
from yt_dlp import YoutubeDL
import youtube_search

def read_shazam_track_ids():
  # Read the CSV file
  file_path = sys.argv[1]
  df = pd.read_csv(file_path, skiprows=1)
  
  # Extract the Track IDs
  return df['TrackKey'].unique().tolist()

def yt_search(name):

  with youtube_search.YoutubeSearch() as ytsearch:
    print(f"Searching for {name}")
    ytsearch.search(name)
    result = ytsearch.list()[0]
    (title, id) = (result['title'], result['id'])
    print(title, " - ", id)

  return id


async def main():
  track_ids = read_shazam_track_ids()

  shazam = Shazam()
  yt_ids = []
  for track_id in track_ids:
    try:
      about_track = await shazam.track_about(track_id=track_id)
      serialized = Serialize.track(data=about_track)
      # searching for 'title - subtitle' which converts to 'singer - song'
      name = serialized.title + " - " + serialized.subtitle
      yt_ids.append(yt_search(name))
    except Exception as e:
      print(e.message, e.args)

  ydl_opts = {
    'format': 'mp3/bestaudio/best',
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }]
  }

  with YoutubeDL(ydl_opts) as ydl:
    ydl.download(list(map(lambda id: f"https://www.youtube.com/watch?v={id}", yt_ids)))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


