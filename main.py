import requests

def get_albums(id):

    albums = []
    url = f'https://music.yandex.ru/artist/{id}/albums'
    result = requests.get(url=url)
    if result.status_code != 200:
        print('Shit happens')
        exit()
    print('Let\'s go')
    # Убираю лишнее
    start_position = result.text.find('Альбомы')
    end_position = result.text.find('Сборники', start_position)
    cutted_string = result.text[start_position:end_position]

    # Считываю ссылку
    while True:
        start_position = cutted_string.find('<a href="/album/')
        if start_position == -1:
            break
        start_position +=  + len('<a href="')
        end_position = cutted_string.find('"', start_position)
        album_link = 'https://music.yandex.ru' + cutted_string[start_position:end_position]
        cutted_string = cutted_string[end_position:]

    # Считываю название альбома
        start_position = cutted_string.find('album__caption">')
        if start_position == -1:
            break
        start_position += len('album__caption">')
        end_position = cutted_string.find('<',start_position)
        album_name = cutted_string[start_position:end_position]
        cutted_string = cutted_string[end_position:]

        # Считываю название исполнителя
        start_position = cutted_string.find('album__artist deco-typo-secondary typo-add" title="')
        if start_position == -1:
            break
        start_position += len('album__artist deco-typo-secondary typo-add" title="')
        end_position = cutted_string.find('"', start_position)
        band_name = cutted_string[start_position:end_position]
        cutted_string = cutted_string[end_position:]

    # Считываю год альбома
        start_position = cutted_string.find('album__year deco-typo-secondary typo-add">')
        if start_position == -1:
            break
        start_position += len('album__year deco-typo-secondary typo-add">')
        end_position = cutted_string.find('<',start_position)
        album_year = cutted_string[start_position:end_position].strip()
        cutted_string = cutted_string[end_position:]

        albums.append({'band':band_name, 'name':album_name, 'year':album_year, 'URL':album_link})
    return albums

print(get_albums(10899))