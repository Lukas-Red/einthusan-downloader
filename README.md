# Einthusan Movie Downloader

Python CLI tool used to download movies from the Einthusan streaming service.


## Requirements

- Python 3.10+
- FFmpeg installed and in your PATH environment. See the 'How it works' section below.


## Installation
```bash
git clone https://github.com/user/my-repo
cd my-repo
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Download one movie from its URL and save it to ~/Downloads

```bash
python3 einthusan_downloader.py _MOVIE_URL_
```

Download a movie from its URL and use yt-dlp to combine the stream segments:

```bash
python3 einthusan_downloader.py _MOVIE_URL_ -m yt-dlp
```

Download 3 movies and save them to /my/favorite/folder

```bash
python3 einthusan_downloader.py _MOVIE1_URL_ _MOVIE2_URL_ -o /my/favorite/folder _MOVIE3_URL_
```

!EXPERIMENTAL! Download a movie with the URL copied in your clipboard

```bash
python3 einthusan_downloader.py
```


## How it works

The goal of the tool is to obtain the m3u8 playlist of each movie URL provided. It does so by mimicking some of the requests a browser would do to obtain the stream playlist.

Once the m3u8 playlist has been obtained, it's saved in a local file, and used by a video processing tool like ffmpeg to download the individual .ts segments listed and combine them into one video file.

For this reason, using the tool requires a video processing tool like FFmpeg that can take an m3u8 file as input. The script natively supports yt-dlp as well, though that tool itself requires FFmpeg to work.

To use the script with another or your own video processor, add an entry for it in ```video_combiner.json```. Only the 2 binding variables already in use are supported.


## Disclaimer

As of publishing this, these are the terms of service of Einthusian:
https://einthusan.tv/terms/

Use this script responsibly and at your own risk.
