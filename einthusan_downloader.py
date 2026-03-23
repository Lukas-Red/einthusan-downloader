from random import randint
import os
import argparse
import json
import pathlib
from time import time

import einthusan_endpoints
import video_combiner
import clipboard_reader

desc = 'CLI tool that downloads movies from einthusan. Requires another CLI tool to combine the' \
'.ts segments into a single video file. The default ones are ffmpeg and yt-dlp. You can modify' \
'video_combiners.json to add another such tool.'

default_method_key = 'yt-dlp'
downloads_folder = os.path.join(pathlib.Path.home(), 'Downloads')

parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    'urls', 
    nargs='*', 
    metavar='URL', 
    help=f'One or more einthusian URLs'
)
parser.add_argument(
    '-m', 
    '--method', 
    default=default_method_key, 
    help='The CLI tool to combine the .ts videos. ' \
    f'The tool you use must be configured in video_combiners.json. default: {default_method_key}'
)
parser.add_argument(
    '-o',
    '--output-dir',
    default=downloads_folder,
    help=f'Folder where the movies will be saved. Default: {downloads_folder}'
)

args = parser.parse_args()

# Experimental, favor using the arguments instead
urls = args.urls
if not urls:
    urls = [clipboard_reader.read_clipboard()]

base_path = os.path.dirname(os.path.realpath(__file__))

user_agents = open(os.path.join(base_path, 'user-agents.txt'), 'r').read().splitlines()
user_agent = user_agents[randint(0, len(user_agents)-1)]

vid_combiner = video_combiner.VideoCombiner(os.path.join(base_path, 'video_combiners.json'), args.method)

# TODO add exception handling in this loop
for movie_url in args.urls:

    print(f'\n\nStarting download process for {movie_url}\n')

    client = einthusan_endpoints.EinthusianClient(movie_url=movie_url, user_agent=user_agent)

    m3u8_data = client.get_movie_playlist()
    movie_name = client.get_movie_name()
    movie_output = os.path.join(args.output_dir, f'{movie_name}.mp4')
    i = 2
    while os.path.isfile(movie_output):
        movie_output = os.path.join(args.output_dir, f'{movie_name}_{i}.mp4')
        i += 1
    
    # write the m3u8 data in a precise timestamp, no chance of file e
    m3u8_path = os.path.join(base_path, f'{str(time()).replace('.', '')}.m3u8')
    with open(m3u8_path, 'w') as fp:
        fp.write(m3u8_data)
    vid_combiner.combine_video_from_m3u8_file(m3u8_path=m3u8_path, output_file=movie_output)


print('All downloads completed. Exiting')
exit(0)