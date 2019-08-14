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

def get_all_viewed_movies(user_id):
    film_id = []
    request = requests.Session()
    url = "https://www.kinopoisk.ru/graph_data/last_vote_data/" + str(user_id)[-3:] + "/last_vote_" + str(user_id) + "__films.json"
    response = request.get(url, headers=HEADERS)
    response.connection.close()
    contents = response.content.decode('utf-8', 'ignore')
    contents = contents[contents.find("["):-1]
    contents = json.loads(contents)
    for content in contents:
        film_id.append(content.get("url")[6:-1])
    return film_id
