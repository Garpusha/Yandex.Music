import requests

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

        albums.append({'band':band, 'name':album_name, 'year':album_year, 'URL':album_link})
    return albums

def write_to_file(my_list, filename):
    with open(filename, 'w', encoding='utf32') as my_file:
        for element in my_list:
            for value in element.values():
                my_string = f'{value};'
                my_file.write(my_string)
            my_file.write('\n')

id = input('Enter musician ID (could be found at music.yandex.ru): ')
write_to_file(get_albums(id),f'{id} albums.csv')