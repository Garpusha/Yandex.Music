import requests
import configparser
from random import randint

def set_to_str(my_set):
    result_str = ''
    for index, item in enumerate(my_set):
        temp_str = ''
        temp_str = f'{index + 1};{temp_str}{str(item)}\n'
        result_str = result_str + temp_str
    return result_str

def parse_track(track_details):
    my_list = []
    my_list.append(track_details[1:11])
    my_list[0] = int(my_list[0][2:4]) * 3600 + int(my_list[0][5:7]) * 60 + int(my_list[0][8:10])

    s_str = '"name":"'
    s_pos = track_details.find(s_str)
    e_pos = track_details.find('","url":"', s_pos + len(s_str))
    my_list.append(track_details[s_pos + len(s_str):e_pos])

    s_str = '","url":"'
    s_pos = track_details.find(s_str)
    my_list.append(track_details[s_pos + len(s_str):-1])

    # my_list[1] = my_list[1][8:-1]
    # my_list[2] = my_list[2][7:-1]
    return {'name':my_list[1], 'length':my_list[0], 'URL':my_list[2]}

def get_tracks(album_url, min_tracks):
    tracks = []
    result = requests.get(url=album_url)
    if result.status_code != 200:
        print('Shit happens')
        exit()
    cutted_string = result.text

    # Читаю количество треков в альбоме
    search_str = '"numTracks":'
    start_position = cutted_string.find(search_str)
    end_position = cutted_string.find(',', start_position + len(search_str))
    tracks_no = int(cutted_string[start_position + len(search_str):end_position])
    if tracks_no < min_tracks:
        return None, None, None
    cutted_string = cutted_string[end_position:]
    print(f'{tracks_no} tracks' )

    # Читаю жанр
    search_str = '"genre":"'
    start_position = cutted_string.find(search_str)
    end_position = cutted_string.find('"', start_position + len(search_str))
    genre = cutted_string[start_position + len(search_str):end_position]
    cutted_string = cutted_string[end_position:]

    for index in range(tracks_no):
        search_str = '{"@type":"MusicRecording","duration":'
        start_position = cutted_string.find(search_str)
        end_position = cutted_string.find('}', start_position + len(search_str))
        line_for_parse = cutted_string[start_position + len(search_str):end_position]
        cutted_string = cutted_string[end_position:]
        tracks.append(parse_track(line_for_parse))
    return tracks, genre, tracks_no


def read_config(path, section, parameter):
    config = configparser.ConfigParser()
    config.read(path)
    c_value = config.get(section, parameter)
    return c_value

def get_albums(id_string):

    band_id, album_id, genre_id = 0, 0, 0
    albums = []
    url = f'https://music.yandex.ru/artist/{id_string}/albums'
    result = requests.get(url=url)
    if result.status_code != 200:
        print('Shit happens')
        exit()

    # Ищу название исполнителя
    search_str = 'page-artist__title typo-h1 typo-h1_big">'
    start_position = result.text.find(search_str)
    end_position = result.text.find('<', start_position + len(search_str))
    band = result.text[start_position+len(search_str):end_position]
    print(band)

    # Убираю лишнее
    start_position = result.text.find('Альбомы')
    end_position = result.text.find('Сборники', start_position)
    cutted_string = result.text[start_position:end_position]
    counter = 0

    # Считываю ссылку
    while True:
        search_str = '<a href="/album/'
        start_position = cutted_string.find(search_str)
        if start_position == -1:
            break
        start_position += len(search_str)
        end_position = cutted_string.find('"', start_position)
        album_link = 'https://music.yandex.ru/album/' + cutted_string[start_position:end_position]
        cutted_string = cutted_string[end_position:]

    # Считываю название альбома
        search_str = 'album__caption">'
        start_position = cutted_string.find(search_str)
        if start_position == -1:
            break
        start_position += len(search_str)
        end_position = cutted_string.find('<',start_position)
        album_name = cutted_string[start_position:end_position]
        cutted_string = cutted_string[end_position:]

        # Считываю название исполнителя
        # search_str = 'album__artist deco-typo-secondary typo-add" title="'
        # start_position = cutted_string.find(search_str)
        # if start_position == -1:
        #     break
        # start_position += len(search_str)
        # end_position = cutted_string.find('"', start_position)
        # band_name = cutted_string[start_position:end_position]
        # cutted_string = cutted_string[end_position:]

    # Считываю год альбома
        search_str = 'album__year deco-typo-secondary typo-add">'
        start_position = cutted_string.find(search_str)
        if start_position == -1:
            break
        start_position += len(search_str)
        end_position = cutted_string.find('<',start_position)
        album_year = cutted_string[start_position:end_position].strip()
        cutted_string = cutted_string[end_position:]
        # Вставить считывание жанров и обработку треков

    # Считываю названия треков в альбоме, их количество, жанр альбома (исполнителя)
        print(f'Found album: {album_name} ({album_year})')
        mintracks = int(read_config('config.ini', 'Main', 'SkipIfTracksLessThan'))
        my_tracks, my_genre, my_tracks_num = get_tracks(album_link, mintracks)

        # Исключаю синглы
        if my_tracks_num:
            albums.append({'band':band, 'name':album_name, 'year':album_year, 'genre':my_genre, 'tracks_num':my_tracks_num, 'URL':album_link, 'tracks':my_tracks})
    print(f'{len(albums)} albums total')
    return albums


def write_to_file(my_list):
    albums_file = open('albums.csv', 'w', encoding='utf-8')
    tracks_file = open('tracks.csv', 'w', encoding='utf-8')
    band_set = set()
    genre_set = set()
    my_string = 'BandName;AlbumName;AlbumYear;AlbumGenre;TracksInAlbum;URL\n'
    albums_file.write(my_string)
    my_string = 'BandName;AlbumName;TrackName;TrackLength;URL\n'
    tracks_file.write(my_string)
    album_index, track_index = 0, 0
    for band in my_list:
        for album in band:
            album_index += 1
            my_string = f'{album_index};{album["band"]};{album["name"]};{album["year"]};{album["genre"]};{album["tracks_num"]};{album["URL"]}\n'
            albums_file.write(my_string)
            band_set.add(album['band'])
            genre_set.add(album['genre'])
            for track in album['tracks']:
                track_index += 1
                my_string = f'{track_index};{album["band"]};{album["name"]};{track["name"]};{track["length"]};{track["URL"]}\n'
                tracks_file.write(my_string)
    albums_file.close()
    tracks_file.close()
    with open('genres.csv', 'w', encoding='utf-8') as genres_file:
        genres_file.write(set_to_str(genre_set))
    with open('bands.csv', 'w', encoding='utf-8') as bands_file:
        bands_file.write(set_to_str(band_set))

    # Создаю сборники
    collections = int(read_config('config.ini', 'Main', 'Collections'))
    collection_name = read_config('config.ini', 'Main', 'CollectionName')
    tracks_per_collection = int(read_config('config.ini', 'Main', 'TracksPerCollection'))
    with open('collections.csv', 'w', encoding='utf-8') as collections_file:
        for index in range(collections):
            collections_file.write(f'{index + 1};{collection_name}{index + 1}\n')
    # создаю смежную таблицу сборник-трек

    tracks_in_collection = set()
    with open('collection-track.csv', 'w', encoding='utf-8') as collection_track:
        for index in range(collections):
            while len(tracks_in_collection) != tracks_per_collection:
                tracks_in_collection.add(randint(1, track_index))
            for index_2 in tracks_in_collection:
                collection_track.write(f'{index + 1};{index_2}\n')
            print(f'Collection #{index + 1} created')
    return

# start here ------------------------------------------------------------------------------

discography = []
bands_list = read_config('config.ini', 'Main', 'BandID').split(',')

# while True:
#     id = input('Enter musician ID (could be found at music.yandex.ru), \'0\' to finish or empty string to abort: ')
#     if not id or not id.isnumeric():
#         print('Aborting')
#         exit()
#     if id == '0':
#         break
for band_id in bands_list:
    discography.append(get_albums(band_id))
write_to_file(discography)
