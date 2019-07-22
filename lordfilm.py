import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://lordfilms.tv/',
    'Cookie': '__cfduid=d56e14a2fb08592a59c3faddc0acf59ce1553374252; _'
              'ym_uid=1553374254663854114; _ym_d=1553374254; PHPSESSID=90be9pln9uutu1397os208o1p3; _'
              'ym_isad=1; _ym_wasSynced=%7B%22time%22%3A1557084212174%2C%22params%22%3A%7B%22eu%22%3'
              'A0%7D%2C%22bkParams%22%3A%7B%7D%7D; _ym_visorc_51186131=b',
    'X-Requested-With':'XMLHttpRequest',
}

def SearchURLMovies(name):
    DATA = {
        'query': name,
    }

    response = requests.post('http://lordsfilm.tv/engine/mod_punpun/dle_search/ajax/dle_search.php', headers = HEADERS, data = DATA)
    content = response.content.decode('utf-8')
    content = content[content.find('http'):content.find('html') + 4]
    # response = requests.get(content,headers=HEADERS)
    # if (response.status_code != 200):
    #     return staticcontent
    # content = response.content.decode('utf-8')
    # ref = '&ref=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJyZWZfaG9zdCI6ImxvcmRmaWxtcy50diIsInJlcV9ob3N0Ijoic3RyZWFtdG9qdXBpdGVyLm1lIiwiZXhwIjoxNTYxNzI3OTExLCJ0b2tlbiI6ImIxNzYwMDExMTlhYzRhMTgifQ.m9mrXEC9ojXX7cVR5Byedbea2h7-ELkC1vTw01bx3sI'
    # start = '<iframe src='
    # while content.find(start)>-1:
    #     content = content[content.find(start)+len(start):]
    #     newcontent = content[:content.find('>')]
    #     if newcontent.find('width="610"')>-1:
    #         content = newcontent
    #         content = content[content.find('"')+1:]
    #         content = content[:content.find('"')]+ref
    #         return content
    return content