import json
import os
import random
from itertools import chain

num_priorities = 20

def create_library(path):
    music_subdirectories = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    library = {
        'categories': {},
        'weights': [0 for i in range(num_priorities)]
    }

    for subdirectory in music_subdirectories:
        music_file_names = [file_path for file_path in os.listdir(os.path.join(path, subdirectory))
                            if os.path.isfile(os.path.join(path, subdirectory, file_path))
                            and os.path.splitext(file_path)[1] == '.mp3']
        library['categories'][subdirectory] = []

        for music_file_name in music_file_names:
            music_file_path = os.path.abspath(os.path.join(path, subdirectory, music_file_name))
            split_name = music_file_name.split('-')
            print(split_name)
            artist_name = split_name[0].strip()
            song_name = split_name[1].split('.')[0].strip()
            song_dict = {
                'artist_name': artist_name,
                'song_name': song_name,
                'file_path': music_file_path,
                'priority': 0,
                'number_of_repeats': 0
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

    # go through old library and copy priorities over
    for category in old_library['categories'].keys():
        if category in library['categories'].keys():
            for song in old_library['categories'][category]:
                copy_over_priority(song, library['categories'][category])

    library['weights'] = old_library['weights']

    return library


def get_updated_library_keep_repeats(old_library, library_path):
    library = create_library(library_path)

    # go through old library and copy priorities over
    for category in old_library['categories'].keys():
        if category in library['categories'].keys():
            for song in old_library['categories'][category]:
                copy_over_priority_and_repeats(song, library['categories'][category])

    library['weights'] = old_library['weights']

    return library


def reset_repeats(library):
    for category in library['categories'].keys():
        for song in category:
            song['number_of_repeats'] = 0


def copy_over_priority(song_to_copy_priority, category_songs):
    songs_to_modify_priority = [song for song in category_songs
                                if song['artist_name'] == song_to_copy_priority['artist_name']
                                and song['song_name'] == song_to_copy_priority['song_name']]

    for song in songs_to_modify_priority:
        song['priority'] = song_to_copy_priority['priority']


def copy_over_priority_and_repeats(song_to_copy_priority, category_songs):
    songs_to_modify_priority = [song for song in category_songs
                                if song['artist_name'] == song_to_copy_priority['artist_name']
                                and song['song_name'] == song_to_copy_priority['song_name']]

    for song in songs_to_modify_priority:
        song['priority'] = song_to_copy_priority['priority']
        song['number_of_repeats'] = song_to_copy_priority['number_of_repeats']


def reset_repeat_data(library):
    for song in chain(*library['categories'].values()):
        song['number_of_repeats'] = 0


def pick_random_song_from_library(library):
    valid_priorities = [priority for priority in range(num_priorities)
                        if library['weights'][priority] > 0 and get_number_of_songs_for_priority(library, priority) > 0]
    if not valid_priorities:
        return None

    weights = [library['weights'][priority] for priority in valid_priorities]
    priority = random.choices(valid_priorities, weights)[0]

    songs_with_priority = [song for song in chain(*library['categories'].values()) if song['priority'] == priority]
    lowest_repeats_in_priority = min([song['number_of_repeats'] for song in songs_with_priority])
    available_songs_to_choose = [song for song in songs_with_priority if song['number_of_repeats'] == lowest_repeats_in_priority]

    song = random.choice(available_songs_to_choose)
    song['number_of_repeats'] += 1
    return song


def get_number_of_songs_for_priority(library, priority):
    return len([song for song in chain(*library['categories'].values()) if song['priority'] == priority])


def calculate_relative_frequency(library, number_of_songs_in_playlist):
    relative_frequencies = []
    valid_weights = [library['weights'][priority] for priority in range(num_priorities)
                    if library['weights'][priority] > 0 and get_number_of_songs_for_priority(library, priority) > 0]
    weight_sum = sum(valid_weights)
    for priority in range(num_priorities):
        weight = library['weights'][priority]
        num_songs = get_number_of_songs_for_priority(library, priority)
        try:
            relative_frequency = 1.0 / (weight / weight_sum / num_songs) / number_of_songs_in_playlist
            relative_frequencies.append(relative_frequency)
        except ZeroDivisionError:
            relative_frequencies.append('--')

    return relative_frequencies

def write_song_list(library, file_path):
    relative_frequencies = ['{:.2f}'.format(relative_frequency) if relative_frequency != '--' else '--'
                            for relative_frequency
                            in calculate_relative_frequency(library, 40)]

    with open(file_path, 'w') as file:
        for category in library['categories'].keys():
            file.write(category + '\n')
            for song in library['categories'][category]:
                file.write('{:<15}{:<20} {} - {}\n'.format(f"Priority: {song['priority']}",
                                                   f"Frequency: {relative_frequencies[song['priority']]}",
                                                   f"{song['artist_name']}",
                                                   f"{song['song_name']}"))
            file.write('\n')

def write_song_list_bare(library, file_path):
    with open(file_path, 'w') as file:
        for category in library['categories'].keys():
            file.write('(cat)' + category + '\n')
            for song in library['categories'][category]:
                file.write(f'{song["artist_name"]}-"{song["song_name"]}\n')
            file.write('\n')

def write_song_list_json(library, file_path):
    with open(file_path, 'w') as file:
        json.dump(library, file)



