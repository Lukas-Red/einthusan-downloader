from random import randint
import os
# TODO change later to a better arg system with argparse
import sys
import json

import einthusan_endpoints
import video_combiner

if len(sys.argv) < 2:
       print('Run this program with one or multiple movie urls as the arguments!')

method = 'yt-dlp'
vid_combiner = video_combiner.VideoCombiner('video_combiners.json', method)

base_path = os.path.dirname(os.path.realpath(__file__))
user_agents_file = 'user-agents.txt'

user_agents = open(os.path.join(base_path, user_agents_file), 'r').read().splitlines()
user_agent = user_agents[randint(0, len(user_agents)-1)]


for movie_url in sys.argv[1:]:
    print(f'\n\nStarting download process for {movie_url}\n')
    client = einthusan_endpoints.EinthusianClient(movie_url=movie_url, user_agent=user_agent)
    m3u8_data = client.get_movie_playlist()
    # TODO change to grab movie name from html
    movie_output = os.path.join(base_path, f'{client._movie_id}.mp4')
    m3u8_path = os.path.join(base_path, f'{client._movie_id}_temp.m3u8')
    with open(m3u8_path, 'w') as fp:
        fp.write(m3u8_data)
    vid_combiner.combine_video_from_m3u8_file(m3u8_path=m3u8_path, output_file=movie_output)