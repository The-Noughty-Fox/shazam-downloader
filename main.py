# This project is sponsored by DJ Fuzuli.
# - SoundCloud: https://soundcloud.com/djfuzuli
# - MixCloud: https://www.mixcloud.com/DJFuzuli/

import asyncio
import sys
import os
import traceback
import re
import unicodedata
from functools import reduce

from shazamio import Shazam, Serialize

import pandas as pd
import yt_dlp
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

def get_valid_filename(value):
  return re.sub(r'[\/:*?"<>|\\]', '_', value).strip("-_\n ")

def parse_duration_to_seconds(duration: str):
  return reduce(
    lambda sum, value: sum + 60 ** value[0] * int(value[1]),
    enumerate(duration.split(':')[::-1]),
    0
  )

def pick_best_yt_search_result(results):
  return next((r for r in results if parse_duration_to_seconds(r['duration']) > 4 * 60), results[0])

def yt_search(name):
  with youtube_search.YoutubeSearch() as ytsearch:
    print(f"YouTube: Searching for '{name}'")
    ytsearch.search(name)
    result = pick_best_yt_search_result(ytsearch.list())

  return (result['title'], result['id'])

def remove_log_file_if_exists():
  if os.path.exists(ERROR_LOG_FILE):
    os.remove(ERROR_LOG_FILE)

shazam = Shazam()

async def process_track_id(id, error_counter=0):
  try:
    print(f"Shazam: Reading track information for id {id}")
    about_track = await shazam.track_about(track_id=id)
    serialized = Serialize.track(data=about_track)
    title = serialized.subtitle + " - " + serialized.title

    song_section = next((section for section in serialized.sections if section.type == 'SONG'), None)
    if song_section:
      label = next((m.text for m in song_section.metadata if m.title == 'Label'), None)
    (yt_title, id) = yt_search(title)
    full_title = get_valid_filename(title) if not label else get_valid_filename(f"{title} [{label}]")

    url = f"https://www.youtube.com/watch?v={id}"
    print(f"YouTube: Downloading '{title}'")
    opts = YDL_OPTS.copy()
    opts['outtmpl'] = f"shazamlibrary/{full_title}.%(ext)s"
    with yt_dlp.YoutubeDL(opts) as ydl:
      ydl.download([url])
  except yt_dlp.networking.exceptions.HTTPError as e:
    if error_counter < 3:
      print(f"YouTube: Retrying because {str(e)}")
      process_track_id(id, error_counter + 1)
    else:
      raise e


async def main():
  remove_log_file_if_exists()
  track_ids = read_shazam_track_ids()
  for id in track_ids:
    try:
      await process_track_id(id)
    except Exception as e:
      logf = open(ERROR_LOG_FILE, "a")
      logf.write(f"{traceback.format_exc()}\n")
      logf.close()
      print(e)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


