# Shazam Downloader

This project is sponsored by DJ Fuzuli, and allows to download your whole Shazam library as MP3s on your local computer.
* DJ Fuzuli's [SoundCloud](https://soundcloud.com/djfuzuli)
* DJ Fuzuli's [MixCloud](https://www.mixcloud.com/DJFuzuli/)

## Installation
#### MacOS
1. Install the requirements:
```bash
pip install -r requirements.txt
```
2. Install [FFmpeg](https://ffmpeg.org/download.html):
```bash
brew install ffmpeg
```
3. Run the script. The first argument is the path to the file:
```bash
python main.py shazamlibrary.csv
```

## Shazam Library Download

1. Visit https://shazam.com in your favorite browser.
2. Scroll all the way to the bottom of the page and click the "My Library" link found at the bottom right corner, under Legal.
3. Complete the sign in process normally.
4. Click the Download CSV link found immediately below the My Library banner, on the right.
