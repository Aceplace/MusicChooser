import json
import os
library_path = "E:\CoachYeiter Drive\Cheltenham2019\CheltenhamPlaylists2019\Library"

def create_library(path):
    music_subdirectories = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    library = {'categories':{}}

    for subdirectory in music_subdirectories:
        music_file_names = [file_path for file_path in os.listdir(os.path.join(path, subdirectory))
                            if os.path.isfile(os.path.join(path,subdirectory,file_path))
                            and os.path.splitext(file_path)[1] == '.mp3']
        library['categories'][subdirectory] = []

        for music_file_name in music_file_names:
            music_file_path = os.path.abspath(os.path.join(path,subdirectory,music_file_name))
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

save_library(create_library(library_path), 'library.json')