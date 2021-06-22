import json
import os
import random
import typing
from itertools import chain

# todo(Aceplace): Move this into MusicLibrary as member variable
num_priorities = 20


class SongInfo:
    def __init__(self):
        self.artist_name: str = ''
        self.song_name: str = ''
        self.file_path: str = ''
        self.priority: int = 0
        self.number_of_repeats: int = 0


class MusicLibrary:
    def __init__(self):
        self.categories: typing.Dict[str, typing.List[SongInfo]] = {}
        self.weights: typing.List[int] = [0 for i in range(num_priorities)]


def create_library(path: str) -> MusicLibrary:
    # library = {
    #     'categories': {},
    #     'weights': [0 for i in range(num_priorities)]
    # }
    library = MusicLibrary()

    music_subdirectories: typing.List[str] = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    for subdirectory in music_subdirectories:
        music_file_names: typing.List[str] = [file_path for file_path in os.listdir(os.path.join(path, subdirectory))
                            if os.path.isfile(os.path.join(path, subdirectory, file_path))
                            and os.path.splitext(file_path)[1] == '.mp3']

        library.categories[subdirectory] = []
        for music_file_name in music_file_names:
            music_file_path: str = os.path.join(subdirectory, music_file_name)
            split_name: typing.List[str] = music_file_name.split('-')
            artist_name: str = split_name[0].strip()
            song_name: str = split_name[1].split('.')[0].strip()
            # song_dict = {
            #     'artist_name': artist_name,
            #     'song_name': song_name,
            #     'file_path': music_file_path,
            #     'priority': 0,
            #     'number_of_repeats': 0
            # }
            song_info = SongInfo()
            song_info.artist_name = artist_name
            song_info.song_name = song_name
            song_info.file_path = music_file_path
            library.categories[subdirectory].append(song_info)

    return library


def save_library(library: MusicLibrary, file_name: str):
    with open(file_name, 'w') as file:
        json.dump(to_dict(library), file, indent=4)


def load_library(file_name) -> MusicLibrary:
    with open(file_name, 'r') as file:
        library = from_dict(json.load(file))
    return library


def get_updated_library(old_library: MusicLibrary, library_path: str) -> MusicLibrary:
    library: MusicLibrary = create_library(library_path)

    # go through old library and copy priorities over
    for category in old_library.categories.keys():
        if category in library.categories.keys():
            for song in old_library.categories[category]:
                copy_over_priority(song, library.categories[category])

    library.weights = old_library.weights

    return library


def get_updated_library_keep_repeats(old_library: MusicLibrary, library_path: str) -> MusicLibrary:
    library = create_library(library_path)

    # go through old library and copy priorities over
    for category in old_library.categories.keys():
        if category in library.categories.keys():
            for song in old_library.categories[category]:
                copy_over_priority_and_repeats(song, library.categories[category])

    library.weights = old_library.weights

    return library


def reset_repeats(library: MusicLibrary):
    for category in library.categories.keys():
        for song in library.categories[category]:
            song.number_of_repeats = 0

def reset_repeats_special(library: MusicLibrary):
    songs = [song for song in chain(*library.categories.values())]
    for priority in range(0, num_priorities):
        songs_with_priority = [song for song in songs if song.priority == priority]
        max_repeats = max(song.number_of_repeats for song in songs_with_priority)
        for song in songs_with_priority:
            song.number_of_repeats = 1 if song.number_of_repeats == max_repeats else 0

def reset_repeat_data(library: MusicLibrary):
    for song in chain(*library.categories.values()):
        song.number_of_repeats = 0

def copy_over_priority(song_to_copy_priority: SongInfo, category_songs: typing.List[SongInfo]):
    songs_to_modify_priority = [song for song in category_songs
                                if song.artist_name == song_to_copy_priority.artist_name
                                and song.song_name == song_to_copy_priority.song_name]

    for song in songs_to_modify_priority:
        song.priority = song_to_copy_priority.priority


def copy_over_priority_and_repeats(song_to_copy_priority: SongInfo, category_songs: typing.List[SongInfo]):
    songs_to_modify_priority = [song for song in category_songs
                                if song.artist_name == song_to_copy_priority.artist_name
                                and song.song_name == song_to_copy_priority.song_name]

    for song in songs_to_modify_priority:
        song.priority = song_to_copy_priority.priority
        song.number_of_repeats = song_to_copy_priority.number_of_repeats


def pick_random_song_from_library(library: MusicLibrary) -> typing.Optional[SongInfo]:
    valid_priorities: typing.List[int] = [priority for priority in range(num_priorities)
                        if library.weights[priority] > 0 and get_number_of_songs_for_priority(library, priority) > 0]
    if not valid_priorities:
        return None

    weights = [library.weights[priority] for priority in valid_priorities]
    priority = random.choices(valid_priorities, weights)[0]

    songs_with_priority = [song for song in chain(*library.categories.values()) if song.priority == priority]
    lowest_repeats_in_priority = min([song.number_of_repeats for song in songs_with_priority])
    available_songs_to_choose = [song for song in songs_with_priority if song.number_of_repeats == lowest_repeats_in_priority]

    song_info = random.choice(available_songs_to_choose)
    song_info.number_of_repeats += 1
    return song_info


def get_random_song_path_from_library(library: MusicLibrary) -> str:
    song = pick_random_song_from_library(library)
    if not song:
        return ''
    return song.file_path


def get_number_of_songs_for_priority(library: MusicLibrary, priority: int) -> int:
    return len([song for song in chain(*library.categories.values()) if song.priority == priority])


def calculate_relative_frequency(library: MusicLibrary, number_of_songs_in_playlist: int) -> typing.List[typing.Union[float, str]]:
    relative_frequencies = []
    valid_weights = [library.weights[priority] for priority in range(num_priorities)
                    if library.weights[priority] > 0 and get_number_of_songs_for_priority(library, priority) > 0]
    weight_sum = sum(valid_weights)
    for priority in range(num_priorities):
        weight = library.weights[priority]
        num_songs = get_number_of_songs_for_priority(library, priority)
        try:
            relative_frequency = 1.0 / (weight / weight_sum / num_songs) / number_of_songs_in_playlist
            relative_frequencies.append(relative_frequency)
        except ZeroDivisionError:
            relative_frequencies.append('--')

    return relative_frequencies


def write_song_list(library: MusicLibrary, file_path: str):
    relative_frequencies = ['{:.2f}'.format(relative_frequency) if relative_frequency != '--' else '--'
                            for relative_frequency
                            in calculate_relative_frequency(library, 40)]

    with open(file_path, 'w') as file:
        for category in library.categories.keys():
            file.write(category + '\n')
            for song in library.categories[category]:
                file.write('{:<15}{:<20} {} - {}\n'.format(f"Priority: {song.priority}",
                                                   f"Frequency: {relative_frequencies[song.priority]}",
                                                   f"{song.artist_name}",
                                                   f"{song.song_name}"))
            file.write('\n')


def write_song_list_bare(library: MusicLibrary, file_path: str):
    with open(file_path, 'w') as file:
        for category in library.categories.keys():
            file.write('(cat)' + category + '\n')
            for song in library.categories[category]:
                file.write(f'{song.artist_name}-"{song.song_name}\n')
            file.write('\n')


def write_song_list_json(library: MusicLibrary, file_path: str):
    with open(file_path, 'w') as file:
        json.dump(to_dict(library), file)


def to_dict(ml: MusicLibrary) -> typing.Any:
    assert(isinstance(ml, MusicLibrary))

    obj_categories = {}
    for ml_category, ml_category_songs_infos in ml.categories.items():
        categories_song_infos = []
        for ml_song_info in ml_category_songs_infos:
            obj_song_info = {
                'song_name': ml_song_info.song_name,
                'artist_name': ml_song_info.artist_name,
                'priority': ml_song_info.priority,
                'file_path': ml_song_info.file_path,
                'number_of_repeats': ml_song_info.number_of_repeats,
            }
            categories_song_infos.append(obj_song_info)
        obj_categories[ml_category] = categories_song_infos

    obj_weights = ml.weights

    obj_ml = {
        'categories': obj_categories,
        'weights': obj_weights
    }

    return obj_ml


def from_dict(obj) -> MusicLibrary:
    ml_object = MusicLibrary()

    for obj_category, obj_song_infos in obj['categories'].items():
        ml_category_song_infos = []
        for obj_song_info in obj_song_infos:
            ml_song_info = SongInfo()
            ml_song_info.song_name = obj_song_info['song_name']
            ml_song_info.artist_name = obj_song_info['artist_name']
            ml_song_info.priority = obj_song_info['priority']
            ml_song_info.file_path = obj_song_info['file_path']
            ml_song_info.number_of_repeats = obj_song_info['number_of_repeats']
            ml_category_song_infos.append(ml_song_info)
        ml_object.categories[obj_category] = ml_category_song_infos

    ml_object.weights = obj['weights']

    return ml_object
