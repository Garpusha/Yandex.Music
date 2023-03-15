import requests

def set_to_str(my_set):
    temp_str = ''
    for item in my_set:
        temp_str = f'{temp_str}{str(item)}\n'
    return temp_str

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

def get_tracks(album_url):
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
    if tracks_no < 6:
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
        my_tracks, my_genre, my_tracks_num = get_tracks(album_link)

        # Исключаю синглы
        if my_tracks_num:
            albums.append({'band':band, 'name':album_name, 'year':album_year, 'genre':my_genre, 'tracks_num':my_tracks_num, 'URL':album_link, 'tracks':my_tracks})
    print(f'{len(albums)} albums total')
    return albums


def write_to_file(my_list):
    albums_file = open('albums.csv', 'w', encoding='utf-8')
    tracks_file = open('tracks.csv', 'w', encoding='utf-8')
    genres_file = open('genres.csv', 'w', encoding='utf-8')
    bands_file = open('bands.csv', 'w', encoding='utf-8')
    band_set = set()
    genre_set = set()
    my_string = 'BandName;AlbumName;AlbumYear;AlbumGenre;TracksInAlbum;URL\n'
    albums_file.write(my_string)
    my_string = 'BandName;AlbumName;TrackName;TrackLength;URL\n'
    tracks_file.write(my_string)
    for band in my_list:
        for album in band:
            my_string = f'{album["band"]};{album["name"]};{album["year"]};{album["genre"]};{album["tracks_num"]};{album["URL"]}\n'
            albums_file.write(my_string)
            band_set.add(album['band'])
            genre_set.add(album['genre'])
            for track in album['tracks']:
                my_string = f'{album["band"]};{album["name"]};{track["name"]};{track["length"]};{track["URL"]}\n'
                tracks_file.write(my_string)
    albums_file.close()
    tracks_file.close()
    genres_file.write(set_to_str(genre_set))
    bands_file.write(set_to_str(band_set))
    genres_file.close()
    bands_file.close()
    return

# start here ------------------------------------------------------------------------------

discography = []
while True:
    id = input('Enter musician ID (could be found at music.yandex.ru), \'0\' to finish or empty string to abort: ')
    if not id or not id.isnumeric():
        print('Aborting')
        exit()
    if id == '0':
        break
    discography.append(get_albums(id))
write_to_file(discography)