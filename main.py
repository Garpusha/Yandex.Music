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
    return my_list[1], my_list[0], my_list[2]

def create_collections(c_name, c_num, c_size, tracks_num):
    c_list, c_t_list, t_list = [], [], []
    t_set = set()
    for index_1 in range(c_num):
        c_list.append({'id':index_1 + 1, 'collection_name':c_name + str(index_1)})
        while len(t_set) != c_size:
            t_set.add(str(randint(1, tracks_num)))
        t_list = list(t_set)
        for index_2 in range(c_size):
            c_t_list.append({'id':index_2 + 1,'collection_id':index_1 + 1, 'track_id': t_list[index_2]})
    return c_list, c_t_list

def write_to_file(my_list, file_name):
    my_string = ''
    with open(file_name, 'w', encoding='utf-8') as my_file:
        for record in my_list:
            my_string = ';'.join(list(record.values()))
            my_string = my_string + '\n'
            my_file.write(my_string)

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

genre_id, band_id, album_id, track_id = 0, 0, 0, 0
band_genre_id, band_album_id = 0, 0

genres, bands, albums, tracks, collections = [], [], [], [], []
band_genre, band_album, collection_track = [], [], []

# Reading html pages:

for band_id in band_list:
    band_url = f'https://music.yandex.ru/artist/{band_id}/albums'
    band_page = get_page(band_url)
    band_page = band_page[band_page.find('Альбомы'): band_page.find('Сборники')]
    band_page, cut_position = parse_html(band_page, 'page-artist__title typo-h1 typo-h1_big">', '<')
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
            genres.append({'id':genre_id, 'genre_name':genre_name})

        for index in range(tracks_num):
            track_string, cut_position = parse_html(album_page, '{"@type":"MusicRecording","duration":', '}')
            album_page = album_page[cut_position:]
            track_name, track_length, track_url = parse_track(track_string)
            track_id += 1
            tracks.append({'id':track_id, 'track_name':track_name, 'track_length':track_length, 'album_id':album_id})
        print(f'Tracks found: {tracks_num}')
    band_genre_id += 1
    band_genre.append({'id':band_genre_id, 'band_id':band_id, 'genre_id':genre_id})
    collections, collection_track = create_collections(collection_name, collections_no, tracks_per_collection, track_id)

    write_to_file(genres, 'genres.csv')
    write_to_file(albums, 'albums.csv')
    write_to_file(bands, 'bands.csv')
    write_to_file(tracks, 'tracks.csv')
    write_to_file(collections, 'collections.csv')
    write_to_file(band_album, 'band_album.csv')
    write_to_file(band_genre, 'band_genre.csv')
    write_to_file(collection_track, 'collection_track.csv')
    print(f'Job dode.\n Bands: {band_id}\nAlbums: {album_id}\nTracks: {track_id}\nGenres: {genre_id}\nCollections: {collections_no}')









