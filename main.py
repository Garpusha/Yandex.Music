import requests
import configparser
from random import randint

def get_page(page_url):
    result = requests.get(url=page_url)
    if result.status_code != 200:
        print('Shit happens')
        exit()
    print(f'Reading {page_url} -- OK)
    return result.text

def read_config(path, section, parameter):
    config = configparser.ConfigParser()
    config.read(path)
    c_value = config.get(section, parameter)
    return c_value

def parse_html(raw_text, start_seq, end_seq):
    # search_str = '<a href="/album/'
    start_position = raw_text.find(start_seq)
    if start_position == -1:
        return None
    start_position += len(start_seq)
    end_position = raw_text.find(end_seq, start_position)
    return raw_text[start_position:end_position], end_position

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
    return my_list[1], my_list[0], my_list[2]











def set_to_str(my_set):
    result_str = ''
    for index, item in enumerate(my_set):
        temp_str = ''
        temp_str = f'{index + 1};{temp_str}{str(item)}\n'
        result_str = result_str + temp_str
    return result_str



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
# Reading config

band_list = read_config('config.ini', 'Main', 'BandID').split(',')
collections_no = int(read_config('config.ini', 'Main', 'Collections'))
collection_name = read_config('config.ini', 'Main', 'CollectionName')
tracks_per_collection = int(read_config('config.ini', 'Main', 'TracksPerCollection'))
min_tracks = int(read_config('config.ini', 'Main', 'SkipIfTracksLessThan'))

# Structure:
# genre = {'genre_id':, 'genre_name':}
# band = {'band_id':, 'band_name':, 'band_url':}
# album = {'album_id':, 'album_name':, 'album_year':, 'album_url':}
# track = {'track_id':, 'track_name':, 'track_length':, 'track_url':, 'album_id':}
# collection = {'collection_id':, 'collection_name':, 'collection_year':}
# band_genre = {'band_genre_id':, 'band_id':, 'genre_id':}
# band_album = {'band_album_id':, 'band_id':, 'album'_id':'}
# collection_track = {'collection_track_id':, 'collection_id', 'track_id':}

genre_id, band_id, album_id, track_id, collection_id = 0, 0, 0, 0, 0
genres, bands, albums, tracks, collections = [], [], [], [], []
band_genre_id, band_album_id, collection_track_id = 0, 0, 0
band_genre, band_album, collection_track = [], [], []

# Reading html pages:

for band_id in band_list:
    band_url = f'https://music.yandex.ru/artist/{band_id}/albums'
    band_page = get_page(band_url)
    band_page = band_page[band_page.find('Альбомы'): band_page.find('Сборники')]
    band_page, cut_position  = parse_html(band_page, 'page-artist__title typo-h1 typo-h1_big">', '<')
    band_page = band_page[cut_position:]
    band_id += 1
    bands.append({'id':band_id, 'band_name':band_name, 'band_url':band_url})
    print(f'Musician found: {band_name}')

    while True:
        album_url, cut_position = parse_html(band_page, '<a href="/album/', '"')
        if album_url == None:
            break
        album_url = 'https://music.yandex.ru/album/' + album_url
        band_page = band_page[cut_position:]
        album_name, cut_position = parse_html(band_page, 'album__caption">', '<')
        band_page = band_page[cut_position:]
        album_year, cut_position = parse_html(band_page, 'album__year deco-typo-secondary typo-add">', '<')
        album_year = int(album_year)
        band_page = band_page[cut_position:]

        album_page = get_page(album_url)
        tracks_num, cut_position = parse_html(album_page, '"numTracks":', ',')
        tracks_num = int(tracks_num)
        album_page = album_page[cut_position:]
        if tracks_num < min_tracks:
            pass
        album_id += 1
        albums.append({'id': album_id, 'album_name': album_name, 'album_year':album_year, 'album_url':album_url})
        band_album_id += 1
        band_album.append({'id':band_album_id, 'band_id':band_id, 'album_id':album_id})
        print(f'Album found: {album_year} - {album_name}')

        genre_name, cut_position = parse_html(album_page, '"genre":"', '"')
        album_page = album_page[cut_position:]
        is_genre = False
        for genre in genres:
            if genre_name == genre['genre_name']:
                is_genre = True
                break
        if not is_genre:
            genre_id += 1
            genre.append({'id':genre_id, 'genre_name':genre_name})

        for index in range(tracks_num):
            track_string, cut_position = parse_html(album_page, '{"@type":"MusicRecording","duration":', '}')
            album_page = album_page[cut_position:]
            track_name, track_length, track_url = parse_track(track_string)
            track_id += 1
            tracks.append({'id':track_id, 'track_name':track_name, 'track_length':track_length, 'album_id':album_id})
        print(f'Tracks found: {tracks_num}')
    band_genre_id += 1
    band_genre.append({'id':band_genre_id, 'band_id':band_id, 'genre_id':genre_id})









discography = []


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

