import requests

def parse_track(track_details):
    my_list = track_details.split(sep=',')
    del my_list[1]
    del my_list[2]
    my_list[0] = int(my_list[0][2:4]) * 3600 + int(my_list[0][5:7]) * 60 + int(my_list[0][8:10])
    my_list[1] = my_list[1][1:-1]
    my_list[2] = my_list[2][1:-1]
    return {'name':my_list[1], 'length':my_list[0], 'URL':my_list[2]}

def get_tracks(album):
    tracks = []
    url = album['URL']
    result = requests.get(url=url)
    if result.status_code != 200:
        print('Shit happens')
        exit()
    print('Looking for tracks')
    cutted_string = result.text

    # Читаю количество треков в альбоме
    search_str = '"numTracks":'
    start_position = cutted_string.find(search_str)
    end_position = cutted_string.find(',', start_position + len(start_position))
    tracks_no = int(cutted_string[start_position:end_position])
    cutted_string = cutted_string[end_position:]

    # Читаю жанр
    search_str = '"genre":"'
    start_position = cutted_string.find(search_str)
    end_position = cutted_string.find('"', start_position + len(start_position))
    genre = cutted_string[start_position:end_position]
    cutted_string = cutted_string[end_position:]

    for index in range(tracks_no):
        search_str = '{"@type":"MusicRecording","duration":'
        start_position = cutted_string.find(search_str)
        end_position = cutted_string.find('}', start_position + len(start_position))
        line_for_parse = cutted_string[start_position:end_position]
        cutted_string = cutted_string[end_position:]
        tracks.append(parse_track(line_for_parse))
    return tracks, tracks_no, genre

def get_albums(id_string):

    albums = []
    url = f'https://music.yandex.ru/artist/{id_string}/albums'
    result = requests.get(url=url)
    if result.status_code != 200:
        print('Shit happens')
        exit()
    print('Let\'s go')

    # Ищу название исполнителя
    search_str = 'page-artist__title typo-h1 typo-h1_big">'
    start_position = result.text.find(search_str)
    end_position = result.text.find('<', start_position + len(search_str))
    band = result.text[start_position+len(search_str):end_position]

    # Убираю лишнее
    start_position = result.text.find('Альбомы')
    end_position = result.text.find('Сборники', start_position)
    cutted_string = result.text[start_position:end_position]

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

        my_tracks, my_genre, my_tracks_num = get_tracks(album_link)
        albums.append({'band':band, 'name':album_name, 'year':album_year, 'genre':my_genre, 'tracks_num':my_tracks_num, 'URL':album_link, 'tracks':my_tracks})
    return albums


def write_to_file(my_list):
    albums_file = open('albums.csv', 'w')
    tracks_file = open('tracks.csv', 'w')
    my_string = 'BandName;AlbumName;AlbumYear;AlbumGenre;TracksInAlbum;URL\n'
    albums_file.write(my_string)
    my_string = 'BandName;AlbumName;TrackName;TrackLength;URL\n'
    for album in my_list:
        my_string = f'{album["band"]};{album["name"]};{album["year"]};{album["genre"]};{album["tracks_num"]};{album["URL"]}\n'
        albums_file.write(my_string)
        for track in album['tracks']:
            my_string = f'{album["band"]};{album["name"]};{track["name"]};{track["length"]};{track["URL"]}\n'
            tracks_file.write(my_string)
    albums_file.close()
    tracks_file.close()

discography = []
while True
    id = input('Enter musician ID (could be found at music.yandex.ru) or \'0\' to exit ')
    if id == '0' or not id:
        exit
    if not id.isnumeric():
        pass
    discography.append(get_albums(id))
write_to_file(discography)