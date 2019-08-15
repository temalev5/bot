import requests
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.1.8) Gecko/20100214 Linux Mint/8 (Helena) Firefox/'
                  '3.5.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3',
    'Accept-Encoding': 'deflate',
    'Accept-Charset': 'windows-1251,utf-8;q=0.7,*;q=0.7',
    'Keep-Alive': '300',
    'Connection': 'keep-alive',
    'Referer': 'http://www.kinopoisk.ru/',
    'Cookie': 'users_info[check_sh_bool]=none; search_last_date=2010-02-19; search_last_month=2010-02;'
              '                                        PHPSESSID=b6df76a958983da150476d9cfa0aab18',
}


def get_url(params):
    all_params = {
        'аниме': 'genre[]=1750&',
        'биография': 'genre[]=22&',
        'биографический': 'genre[]=22&',
        'боевик': 'genre[]=3&',
        'вестерн': 'genre[]=13&',
        'военный': 'genre[]=19&',
        'детектив': 'genre[]=17&',
        'детский': 'genre[]=456&',
        'детей': 'genre[]=456&',
        'документальный': 'genre[]=12&',
        'документалка': 'genre[]=12&',
        'драма': 'genre[]=8&',
        'история': 'genre[]=23&',
        'исторический': 'genre[]=23&',
        'комедия': 'genre[]=6&',
        'комедийный': 'genre[]=6&',
        'короткометражка': 'genre[]=15&',
        'криминал': 'genre[]=16&',
        'криминальный': 'genre[]=16&',
        'мелодрама': 'genre[]=7&',
        'музыка': 'genre[]=21&',
        'музыкальный': 'genre[]=21&',
        'мультфильм': 'genre[]=14&',
        'мультик': 'genre[]=14&',
        'мюзикл': 'genre[]=9&',
        'приключения': 'genre[]=10&',
        'приключенческий': 'genre[]=10&',
        'семейный': 'genre[]=11&',
        'спорт': 'genre[]=24&',
        'спортивный': 'genre[]=24&',
        'триллер': 'genre[]=4&',
        'ужасы': 'genre[]=1&',
        'ужастик': 'genre[]=1&',
        'фантастика': 'genre[]=2&',
        'фантастический': 'genre[]=2&',
        'фильм-нуар': 'genre[]=18&',
        'фэнтези': 'genre[]=5&',
        'россия': 'country[]=2&',
        'россии': 'country[]=2&',
        'российский': 'country[]=2&',
        'руский': 'country[]=2&',
        'русский': 'country[]=2&',
        'сша': 'country[]=1&',
        'американский': 'country[]=1&',
        'ссср': 'country[]=13&',
        'австралия': 'country[]=25&',
        'австралийский': 'country[]=25&',
        'бельгия': 'country[]=41&',
        'великобритания': 'country[]=11&',
        'британия': 'country[]=11&',
        'британский': 'country[]=11&',
        'англия': 'country[]=11&',
        'английский': 'country[]=11&',
        'германия': 'country[]=3&country[]=18&',
        'немецкий': 'country[]=3&country[]=18&',
        'гонконг': 'country[]=28&',
        'дания': 'country[]=4&',
        'индия': 'country[]=29&',
        'индийский': 'country[]=29&',
        'ирландия': 'country[]=38&',
        'ирландский': 'country[]=38&',
        'испания': 'country[]=15&',
        'испанский': 'country[]=15&',
        'италия': 'country[]=14&',
        'итальянский': 'country[]=14&',
        'канада': 'country[]=6&',
        'китай': 'country[]=31&',
        'китайский': 'country[]=31&',
        'южная корея': 'country[]=26&',
        'южно корейский': 'country[]=26&',
        'корея': 'country[]=26&',
        'корейский': 'country[]=26&',
        'южной кореи': 'country[]=26&',
        'франция': 'country[]=8&',
        'французкий': 'country[]=8&',
        'французский': 'country[]=8&',
        'швеция': 'country[]=5&',
        'швецарский': 'country[]=5&',
        'япония': 'country[]=9&',
        'японский': 'country[]=9&',
    }
    url = ""
    for param in params:
        try:
            url += all_params.get(param)
        except:
            pass
    return url


def get_all_viewed_movies(user_id):
    film_id = []
    request = requests.Session()
    url = "https://www.kinopoisk.ru/graph_data/last_vote_data/" + str(user_id)[-3:] + "/last_vote_" + str(
        user_id) + "__films.json"
    response = request.get(url, headers=HEADERS)
    request.close()
    contents = response.content.decode('utf-8', 'ignore')
    contents = contents[contents.find("["):-1]
    contents = json.loads(contents)
    for content in contents:
        film_id.append(content.get("url")[6:-1])
    return film_id


def get_random_movie(params, min_years, max_years):
    request = requests.Session()
    url = 'https://www.kinopoisk.ru/chance/?'
    url += 'item=true&'
    url += 'count=1&'
    url += get_url(params)
    url += 'max_years=' + str(max_years) + '&'
    url += 'min_years=' + str(min_years)
    response = request.get(url)
    request.close()
    content = response.content.decode('utf-8', 'ignore')
    content = content[content.find('content'):]
    content = content[content.find('film')+6:]
    content = content[:content.find("\\")]
    return content
