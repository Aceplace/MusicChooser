import json
import os
import random
from itertools import chain

library_path = "E:\CoachYeiter Drive\Cheltenham2019\CheltenhamPlaylists2019\Library"


def create_library(path):
    music_subdirectories = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    library = {'categories': {}}

    for subdirectory in music_subdirectories:
        music_file_names = [file_path for file_path in os.listdir(os.path.join(path, subdirectory))
                            if os.path.isfile(os.path.join(path, subdirectory, file_path))
                            and os.path.splitext(file_path)[1] == '.mp3']
        library['categories'][subdirectory] = []

        for music_file_name in music_file_names:
            music_file_path = os.path.abspath(os.path.join(path, subdirectory, music_file_name))
            split_name = music_file_name.split('-')
            artist_name = split_name[0].strip()
            song_name = split_name[1].split('.')[0].strip()
            song_dict = {
                'artist_name': artist_name,
                'song_name': song_name,
                'file_path': music_file_path,
                'priority': 1
            }
            library['categories'][subdirectory].append(song_dict)

    return library


def save_library(library, file_name):
    with open(file_name, 'w') as file:
        json.dump(library, file, indent=4)


def load_library(file_name):
    with open(file_name, 'r') as file:
        library = json.load(file)
    return library


def get_updated_library(old_library, library_path):
    library = create_library(library_path)

    #go through old library and copy priorities over
    for category in old_library['categories'].keys():
        if category in library['categories'].keys():
            for song in old_library['categories'][category]:
                copy_over_priority(song, library['categories'][category])

    return library


def copy_over_priority(song_to_copy_priority, category_songs):
    songs_to_modify_priority = [song for song in category_songs
                                if song['artist_name'] == song_to_copy_priority['artist_name']
                                and song['song_name'] == song_to_copy_priority['song_name']]

    for song in songs_to_modify_priority:
        song['priority'] = song_to_copy_priority['priority']


def pick_random_song_from_library(library, priority_weights, repeat_list):
    priority = random.choices([priority_weight[0] for priority_weight in priority_weights],
                              weights=[priority_weight[1] for priority_weight in priority_weights])
    return priority


def get_priority_number_of_songs(library):
    priorities = {song['priority'] for song in chain(*library['categories'].values())}
    song_priorities = [song['priority'] for song in chain(*library['categories'].values())]
    priority_info = [(priority, song_priorities.count(priority)) for priority in priorities]
    return priority_info


def calculate_relative_frequency(priorities, categories_num_songs, weights, number_of_songs_in_playlist):
    relative_frequencies = []
    for priority, num_songs, weight in zip(priorities, categories_num_songs, weights):
        relative_frequency = 1.0 / (weight / sum(weights) / num_songs) / number_of_songs_in_playlist
        relative_frequencies.append((priority, relative_frequency))
    print(relative_frequencies)


library = create_library(library_path)
priority_info = get_priority_number_of_songs(library)
print(priority_info)
calculate_relative_frequency(*zip(*priority_info),[100, 100, 100, 100, 100], 40)

