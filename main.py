# -*- coding: utf-8 -*-
import threading
import time
import vk_api
import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from db import use_db, use_db_for_movies, save_to_db, save_to_db_set, notify_db, save_movies_to_db, save_kp_id
from vk_api.utils import get_random_id
from parse_kp import get_all_viewed_movies
from sm import name_to_id, movie_to_text, get_name_by_id, rating_emoji
import traceback
import os
from lordfilm import search_url_movies

# login, password = "login", "password"
# vk_session = vk_api.VkApi(login, password)
# vk_session.auth()

token = os.environ.get('BOT_TOKEN')
vk_session = vk_api.VkApi(token=token)

session_api = vk_session.get_api()
long_poll = VkBotLongPoll(vk_session, '181453927')


def search_man_for_replace(man_id):
    man = []
    from_replace = False
    for i in range(len(replace_movie)):
        if replace_movie[i].man_id == man_id:
            man = replace_movie[i]
            from_replace = True
    return man, from_replace


def get_chat_title(chat_id):
    try:
        chat_title = session_api.messages.getConversationsById(peer_ids=chat_id + 2000000000)
        chat_title = chat_title.get('items')[0].get('chat_settings').get('title')
        return chat_title
    except:
        return ''


def get_movie_name(movie):
    return movie[:movie.find('(')]


def get_id(movie):
    return movie[movie.find('(') + 1:movie.find(')')]


def list_of_films(movies):
    message = ''
    for i in range(len(movies)):
        message += str(i + 1) + '&#8419; '
        message += movies[i][:movies[i].find(')') + 1] + ' ' \
                   + movies[i][movies[i].find('[') + 1:movies[i].find(']')] \
                   + ';' + '\n'
    return message


def get_username(user_id):
    user_info = session_api.users.get(user_ids=user_id)
    username = user_info[0].get('first_name')
    return username


def checker(one, condition, two):
    if one:
        if two:
            if condition == ">":
                if one >= two:
                    return True
            if condition == ">=":
                if one > two:
                    return True
            if condition == "<":
                if one <= two:
                    return True
            if condition == "<=":
                if one < two:
                    return True
            if condition == "=":
                if one != two:
                    return True
        else:
            return True
    else:
        return False


def check_legitimacy(movie, chat):
    for i in range(len(chat.man)):
        for j in range(len(chat.man[i].movies)):
            if int(get_id(chat.man[i].movies[j])) == movie.id:
                return "Этот фильм уже кто-то заказал!"

    for i in range(len(chat.man)):
        try:
            chat.man[i].ex_movies.index(str(movie.id))
            return get_username(chat.man[i].man_id) + " уже смотрел этот фильм!"
        except:
            pass

    if chat.ex_actors:
        ex_actors = chat.ex_actors.split(';')
        ex_actors.remove("")
        for i in range(len(ex_actors)):
            for j in range(len(movie.actors)):
                if ex_actors[i].lower() == movie.actors[j].name.lower():
                    return "Запрещенный актер &#128253; " + movie.actors[j].name + ' &#128253;'

    if chat.ex_country and movie.countries:
        ex_country = chat.ex_country.split(';')
        ex_country.remove("")
        for i in range(len(ex_country)):
            for j in range(len(movie.countries)):
                if ex_country[i].lower() == movie.countries[j].lower():
                    return "Запрещенная страна &#128253; " + movie.countries[j] + ' &#128253;'

    if chat.ex_genre and movie.genres:
        ex_genre = chat.ex_genre.split(';')
        ex_genre.remove("")
        for i in range(len(ex_genre)):
            for j in range(len(movie.genres)):
                if ex_genre[i].lower() == movie.genres[j].lower():
                    return "Запрещенный жанр &#128253; " + movie.genres[j] + ' &#128253;'

    if checker(chat.ex_rating, chat.ex_rating_condition, movie.rating):
        return "Не подходит по рейтингу &#11088; " + str(movie.rating) + " &#11088;"
    if checker(chat.ex_time, chat.ex_time_condition, movie.runtime):
        return "Не подходит по времени &#11088; " + str(movie.runtime) + " &#11088;"
    if checker(chat.ex_year, chat.ex_year_condition, movie.year):
        return "Не подходит по году создания &#11088; " + str(movie.year) + " &#11088;"


def search_man(man_id):
    man = []
    from_group = False
    try:
        for i in range(len(roll_movie)):
            for j in range(len(roll_movie[i].man)):
                if roll_movie[i].man[j].man_id == man_id:
                    man = roll_movie[i].man[j]
                    from_group = True
        return man, from_group
    except:
        search_man(man_id)


def search_chat(chat_id):
    only = []
    again_movies_roll = False
    try:
        for i in range(len(roll_movie)):
            if roll_movie[i].chat_id == chat_id:
                only = roll_movie[i]
                again_movies_roll = True
        return only, again_movies_roll
    except:
        search_chat(chat_id)


def remove_roll_movie(this, chat_id):
    time.sleep(1800)
    notify_db(chat_id, True)
    if roll_movie.count(this) > 0:
        this.send_films_to_all()
        session_api.messages.send(chat_id=chat_id, message='&#9888; &#9888; &#9888;\n&#10071;'
                                                           ' Сбор фильмов был остановлен. &#10071;\n&#10071;'
                                                           ' Время сбора фильмов вышло. &#10071;\n'
                                                           '&#9888; &#9888; &#9888;',
                                  random_id=get_random_id())
        roll_movie.remove(this)


def check_already_use(man_id, chat_id):
    movies = use_db_for_movies(man_id, chat_id)
    if movies:
        kp_id = movies[0][1]
        movies = movies[0][0]
        movies = movies.split(';')
        return movies, kp_id
    else:
        return [], None


# def Typing(user_id):
# boolTuping = True
# while boolTuping:
# print('успел')
# session_api.messages.setActivity(peer_id=user_id,type = 'typing')
# time.sleep(5)


class Man:

    def __init__(self, chat_id, man_id):
        self.chat_id = chat_id
        self.man_id = man_id
        self.kp_id = None
        self.ex_movies = []
        self.movies = []
        self.searchMovie = None
        self.countFindFilm = 0
        self.targetMovie = None

    def search_movies(self, mov, movie):
        self.searchMovie = mov
        self.targetMovie = movie

    def set_movies(self):
        self.movies.append(self.targetMovie.title + "(" + str(self.targetMovie.id) + ")" + "[" +
                           rating_emoji(self.targetMovie.rating)[:-1] + "]")

    # def get_movies_from_db(self):
    #     use_db_for_movies(self.man_id,self.chat_id)


class ChatRoll:

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.man = []
        self.ex_rating = None
        self.ex_rating_condition = ">"
        self.ex_genre = None
        self.ex_year = None
        self.ex_year_condition = ">"
        self.ex_time = None
        self.ex_time_condition = "<"
        self.ex_actors = None
        self.ex_country = None
        self.notify = True

    def open_db(self):
        result = use_db(self.chat_id)
        if result:
            self.ex_rating = result[0][0]
            if result[0][1]:
                self.ex_rating_condition = result[0][1]
            self.ex_genre = result[0][2]
            self.ex_year = result[0][3]
            if result[0][4]:
                self.ex_year_condition = result[0][4]
            self.ex_time = result[0][5]
            if result[0][6]:
                self.ex_time_condition = result[0][6]
            self.ex_actors = result[0][7]
            self.ex_country = result[0][8]
            if result[0][9] is not None:
                self.notify = result[0][9]

    def new_man(self, chat_id, man_id):
        self.man.append(Man(chat_id, man_id))
        print('Создал нового персонажа без фильмов' + str(man_id))

    def new_man_m(self, chat_id, man_id, movies, kp_id):
        self.man.append(Man(chat_id, man_id))
        self.man[len(self.man) - 1].movies = movies
        self.man[len(self.man) - 1].kp_id = kp_id
        self.man[len(self.man) - 1].ex_movies = get_all_viewed_movies(kp_id)
        print('Создал нового персонажа ' + str(man_id) + str(movies))

    def send_films_to_all(self):
        for i in range(len(self.man)):
            if len(self.man[i].movies) != 0:
                result = save_movies_to_db(self.chat_id, self.man[i].man_id, ";".join(self.man[i].movies))
                if result:
                    message = 'Список фильмов: \n' + list_of_films(self.man[i].movies)
                    session_api.messages.send(peer_id=self.man[i].man_id,
                                              message=message,
                                              random_id=get_random_id())
                else:
                    message = '&#10071; Не удалось сохранить фильмы в БД &#10071;'
                    session_api.messages.send(peer_id=self.man[i].man_id,
                                              message=message,
                                              random_id=get_random_id())

    def roll(self):
        for i in range(len(self.man)):
            print(str(self.man[i].man_id) + str(self.man[i].movies))

        if len(self.man) == 0:
            return '0', '0'

        film_list = 'Список фильмов\n_______________________________________________________________\n'
        ret_list_film = 'СЛУЧАЙНЫЙ ФИЛЬМ:\n&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;' \
                        '&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;' \
                        '&#128293;&#128293;&#128293;\n '
        for i in range(len(self.man)):
            username = get_username(self.man[i].man_id)
            film_list += '***********************\n* ' + username + ' *\n'
            if len(self.man[i].movies) < 2:
                return '0', '&#10071; @id' + str(self.man[i].man_id) + ' (' + username + ') ' \
                                                                                         'скинул мне всего лишь 1 фильм &#10071;'
            elif len(self.man[i].movies) < 3:
                return '0', '&#10071; @id' + str(self.man[i].man_id) + ' (' + username + ') ' \
                                                                                         'должен скинуть мне еще 1 фильм &#10071;'
            elif len(self.man[i].movies) == 3:
                film_list += list_of_films(self.man[i].movies)
        film_list += '***********************\n_______________________________________________________________\n'
        ft_rnd = random.randint(0, len(self.man) - 1)
        sec_rnd = random.randint(0, len(self.man[ft_rnd].movies) - 1)
        remove_movie = self.man[ft_rnd].movies.pop(sec_rnd)

        ret_list_film += movie_to_text(get_name_by_id(int(get_id(remove_movie))))

        url = search_url_movies(get_movie_name(remove_movie))

        ret_list_film += '\n&#9889;' + url + ' &#9889;'

        return film_list, ret_list_film


def film(event, again_movies_roll):
    if again_movies_roll:
        session_api.messages.send(chat_id=event.chat_id, message='&#10071; Сбор фильмов уже начался &#10071;',
                                  random_id=get_random_id())
        return
    else:
        roll_movie.append(ChatRoll(event.chat_id))
        th_rm = roll_movie[len(roll_movie) - 1]
        th_rm.open_db()
        threading.Thread(target=remove_roll_movie, args=(th_rm, event.chat_id,), daemon=True).start()
        message = "&#9888; Начался сбор фильмов &#9888;\n"
        if th_rm.ex_actors or th_rm.ex_country or th_rm.ex_genre or th_rm.ex_rating or th_rm.ex_time or th_rm.ex_year:
            message += "&#10071; Установленные параметры :\n_______________________________\n"
            if th_rm.ex_actors:
                message += "&#128204; Исключенные актеры: &#128253; " + th_rm.ex_actors.replace(';',
                                                                                                ' &#128253; ') + "\n"
            if th_rm.ex_country:
                message += "&#128204; Исключенные страны: &#128253; " + th_rm.ex_country.replace(';',
                                                                                                 ' &#128253; ') + "\n"
            if th_rm.ex_genre:
                message += "&#128204; Исключенные жанры: &#128253; " + th_rm.ex_genre.replace(';', ' &#128253; ') + "\n"
            if th_rm.ex_rating:
                message += "&#128204; Рейтинг " + th_rm.ex_rating_condition + " &#11088; " + str(
                    th_rm.ex_rating) + " &#11088;\n"
            if th_rm.ex_time:
                message += "&#128204; Время " + th_rm.ex_time_condition + " &#11088; " + str(
                    th_rm.ex_time) + " &#11088;\n"
            if th_rm.ex_year:
                message += "&#128204; Год " + th_rm.ex_year_condition + " &#11088; " + str(
                    th_rm.ex_year) + " &#11088;\n"
            message += "_______________________________\n"
        message += "&#10071; Поставь &#128172; [ + ] &#128172; в чат, если готов смотреть &#10071;"
        print('Создал новый класс')
        session_api.messages.send(chat_id=event.chat_id, message=message, random_id=get_random_id())
        if th_rm.notify:
            chat_title = get_chat_title(event.chat_id)
            chat_info = session_api.messages.getConversationMembers(peer_id=event.chat_id + 2000000000)
            for i in range(len(chat_info.get('profiles'))):
                chat_id = chat_info.get('profiles')[i].get('id')
                try:
                    session_api.messages.send(peer_id=chat_id,
                                              message='&#9888; &#9888; &#9888;\n&#128253; '
                                                      'В бесседе &#128173; ' + chat_title + ' &#128173; '
                                                                                            'начался сбор фильмов, скорее ставь &#128172; [ + ] &#128172;'
                                                                                            ', чтобы присоединится. &#128253;\n&#9888; &#9888; &#9888;',
                                              random_id=get_random_id())
                except:
                    print('Не смог отписать' + str(chat_id))
            notify_db(th_rm.chat_id, False)


def ready_to_film(event, again_movies_roll, again_plus, only):
    if again_plus:
        username = get_username(event.obj.from_id)

        message = '&#10071; @id' + str(event.obj.from_id) + ' (' + username + '), уже отписал тебе в лс &#10071;'

        session_api.messages.send(chat_id=event.chat_id, message=message,
                                  random_id=get_random_id())
        return
    else:
        if again_movies_roll:

            try:
                movies, kp_id = check_already_use(event.obj.from_id, event.chat_id)
                print('Принял от ' + str(event.obj.from_id) + str(movies))
                if len(movies) == 0:

                    session_api.messages.send(peer_id=event.obj.from_id,
                                              message='&#128071; Скидывай название первого фильма сюда &#128071;',
                                              random_id=get_random_id())
                    only.new_man(event.chat_id, event.obj.from_id)
                    print('Создал нового персонажа' + str(event.obj.from_id))
                    return
                elif len(movies) <= 3:
                    message = 'Принял от тебя :\n' + list_of_films(movies)
                    if len(movies) < 3:
                        message += '_____________________________\nЖду еще ' + str((3 - len(movies))) + ' &#128253;'
                    else:
                        message += '_____________________________\n&#9745; Принял от тебя все 3 фильма. &#9745;\n&#128253;&#128253;&#128253;\n' \
                                   '&#10071; Тебе доступны команды &#10071;\n&#128172; [ !заменить ' \
                                   '<(название,ID,номер фильма> ] &#128172;\n' \
                                   '&#128172; [ !список ] &#128172;'
                    session_api.messages.send(peer_id=event.obj.from_id,
                                              message=message,
                                              random_id=get_random_id())
                    only.new_man_m(event.chat_id, event.obj.from_id, movies, kp_id)
                    print('Создал нового персонажа' + str(event.obj.from_id) + str(movies))
                    return
            except:
                traceback.print_exc()
                username = get_username(event.obj.from_id)

                message = '&#10071; @id' + str(event.obj.from_id) + \
                          ' (' + username + '), разреши мне писать тебе сообщения\n' \
                                            '&#128495; Для этого перейди в мою группу, кликнув на меня.\n' \
                                            '&#128495; Либо просто напиши мне первый &#10071;'

                session_api.messages.send(chat_id=event.chat_id, message=message,
                                          random_id=get_random_id())


def chat_roll(event, again_movies_roll, only):
    if again_movies_roll:
        film_list, list_film = only.roll()
        if film_list != '0' and list_film != '0':
            session_api.messages.send(chat_id=event.chat_id, message=film_list,
                                      random_id=get_random_id())

            session_api.messages.send(chat_id=event.chat_id, message=list_film,
                                      random_id=get_random_id())

            only.send_films_to_all()
            roll_movie.remove(only)
            return
        else:
            session_api.messages.send(chat_id=event.chat_id, message=list_film,
                                      random_id=get_random_id())
            return
    else:
        session_api.messages.send(chat_id=event.chat_id,
                                  message='&#10071; Для начала необходимо прописать &#128172; [ !фильм ] &#128172; '
                                          'для того, чтобы запустить сбор фильмов.',
                                  random_id=get_random_id())


def stop(event, again_movies_roll, only):
    if again_movies_roll:
        only.send_films_to_all()
        roll_movie.remove(only)
        session_api.messages.send(chat_id=event.chat_id,
                                  message='&#10071; Сбор фильмов остановлен &#10071;',
                                  random_id=get_random_id())
    else:
        session_api.messages.send(chat_id=event.chat_id,
                                  message='&#10071; Для начала необходимо прописать &#128172; [ !фильм ] &#128172; '
                                          'для того, чтобы запустить сбор фильмов.',
                                  random_id=get_random_id())


def del_ret(event):
    t = event.obj.text[:event.obj.text.find(' ')]
    items = session_api.messages.getConversationMembers(peer_id=2000000000 + event.chat_id).get('items')
    for item in items:
        if item.get('member_id') == event.obj.from_id:
            if item.get('is_admin'):
                name = event.obj.text[event.obj.text.find(' ') + 1:]
                name = name[:name.find(' ')].lower()
                if (name == "актера") or (name == "жанр") or (name == "страну"):
                    value = event.obj.text[event.obj.text.find(' ') + 1:]
                    value = value[value.find(' ') + 1:] + ";"
                    validate = save_to_db(event.chat_id, name, value.lower(), t)
                    if not validate:
                        break
                    message = ""
                    what = "Исключен"
                    whats = "доступен"
                    if name == "актера":
                        name = "актер"
                    if name == "страну":
                        name = "страна"
                        what = "Исключена"
                        whats = "доступна"
                    if t == "!исключить":
                        message = "&#128204; " + what + " " + name + ' &#128253; ' + value[:-1] + ' &#128253;'
                    elif t == "!вернуть":
                        message = "&#128204; " + name + ' &#128253; ' + value[
                                                                        :-1] + " &#128253; теперь " + whats + " &#9989;"

                    session_api.messages.send(chat_id=event.chat_id,
                                              message=message,
                                              random_id=get_random_id())


def chat_set(event):
    items = session_api.messages.getConversationMembers(peer_id=2000000000 + event.chat_id).get('items')
    for item in items:
        if item.get('member_id') == event.obj.from_id:
            if item.get('is_admin'):
                name = event.obj.text[event.obj.text.find(' ') + 1:]
                name = name[:name.find(' ')].lower()
                if (name == "рейтинг") or (name == "время") or (name == "год"):
                    condition = event.obj.text[event.obj.text.find(' ') + 1:]
                    condition = condition[condition.find(' ') + 1:]
                    condition = condition[:condition.find(' ')]
                    if (condition == ">") or (condition == "<") or (condition == ">=") or (condition == "<=") or (
                            condition == "="):
                        value = event.obj.text[event.obj.text.find(' ') + 1:]
                        value = value[value.find(' ') + 1:]
                        value = value[value.find(' ') + 1:]
                        save_to_db_set(event.chat_id, name, condition, value)
                        message = "&#128204; Установлен параметр &#128253; " + name + " " + "фильма &#128253; " \
                                  + condition + " &#11088;" + value + " &#11088;"

                        session_api.messages.send(chat_id=event.chat_id,
                                                  message=message,
                                                  random_id=get_random_id())


def replace(event, only):
    remove = None
    try:
        num = int(event.obj.text[10:])
        if num < 1:
            return
        if num < 4:
            try:
                remove = only.movies.pop(num - 1)
            except:
                pass
        else:
            for i in range(len(only.movies)):
                if int(get_id(only.movies[i])) == num:
                    remove = only.movies.pop(i)
                    break
    except:
        num = event.obj.text[10:]
        for i in range(len(only.movies)):
            if get_movie_name(only.movies[i].lower()) == num.lower():
                remove = only.movies.pop(i)
                break
    if remove:
        message = 'Фильм &#128253; ' + get_movie_name(remove) + ' &#128253; был удален\n_____________________________\n'
        message += 'Текущий список фильмов :\n' + list_of_films(only.movies)
        message += '_____________________________\nЖду от тебя фильма на замену.'
    else:
        message = '&#10071; Не удалось удалить фильм &#10071;'
    session_api.messages.send(peer_id=event.obj.from_id,
                              message=message,
                              random_id=get_random_id())


def replace_in_db(event):
    remove = None
    movies = use_db_for_movies(event.obj.from_id, None)
    rm = None
    if movies:
        if event.obj.text.find(' ') > 0:
            if event.obj.text.find(' ') == event.obj.text.rfind(' '):
                try:
                    num = int(event.obj.text[event.obj.text.find(' '):])
                    if num < 1:
                        return
                    if num < 4:
                        movies = movies[0:1]
                        if len(movies) == 1:
                            replace_movie.append(Man(movies[0][0], event.obj.from_id))
                            rm = replace_movie[len(replace_movie) - 1]
                            rm.movies = movies[0][1].split(';')
                            remove = rm.movies.pop(num - 1)
                    else:
                        for movie in movies:
                            mov = movie[1].split(';')
                            for i in range(len(mov)):
                                if int(get_id(mov[i])) == num:
                                    replace_movie.append(Man(movie[0], event.obj.from_id))
                                    rm = replace_movie[len(replace_movie) - 1]
                                    rm.movies = mov
                                    remove = rm.movies.pop(i)
                                    break
                            if rm:
                                break

                except:
                    pass
                a = 10
        else:
            message = 'Список фильмов:\n'
            for i in range(len(movies)):
                message += str(i + 1) + '. &#128253; ' + get_chat_title(movies[i][0]) + ' &#128253;\n'
                message += list_of_films(movies[i][1].split(';'))
                message += '________________________________________\n'
            message += '&#10071; Для того, чтобы заменить напиши: &#10071;\n' \
                       '&#128172; [ !заменить <(id фильма,название фильма)> ] &#128172;\n' \
                       '________________________________________\n' \
                       '&#10071; Если один и тот же фильм находится в разных беседах, ' \
                       'следует воспользоваться формой ниже &#10071;\n' \
                       '&#128172; [ !заменить <(id беседы,название беседы)> <(номер,id,название фильма)> ] &#128172;'
            session_api.messages.send(peer_id=event.obj.from_id,
                                      message=message,
                                      random_id=get_random_id())
            return
    else:
        message = "Не удалось найти фильмы"
        session_api.messages.send(peer_id=event.obj.from_id,
                                  message=message,
                                  random_id=get_random_id())
    if remove:
        message = 'Фильм &#128253; ' + get_movie_name(remove) + ' &#128253; был удален ' \
                                                                'из беседы:\n&#9642; ' + get_chat_title(
            rm.chat_id) + '\n_____________________________\n'
        message += 'Текущий список фильмов :\n' + list_of_films(rm.movies)
        message += '_____________________________\nЖду от тебя фильма на замену.'
    else:
        message = '&#10071; Не удалось удалить фильм &#10071;'
    session_api.messages.send(peer_id=event.obj.from_id,
                              message=message,
                              random_id=get_random_id())


def chat_list(event, only):
    movies = only.movies
    message = 'Текущий список фильмов :\n' + list_of_films(movies)
    session_api.messages.send(peer_id=event.obj.from_id,
                              message=message,
                              random_id=get_random_id())


def reject_movie(event, only, keyboard):
    beh_movie = only.searchMovie
    only.countFindFilm += 1
    movie, message = name_to_id(beh_movie, only.countFindFilm)
    if message != '0':
        only.targetMovie = movie
    else:
        only.countFindFilm = 0
        only.searchMovie = None
        only.targetMovie = None
        session_api.messages.send(peer_id=event.obj.from_id,
                                  message='&#9888; &#9888; &#9888;\n&#10071;'
                                          ' Не смог найти фильм по твоему запросу &#10071;\n'
                                          '&#129300; Наверняка у него другое название, попробуй еще &#129300;\n'
                                          '&#9888; &#9888; &#9888;\n',
                                  random_id=get_random_id())
        return
    message += 'Это он?&#129300; Отпиши + или -'

    session_api.messages.send(peer_id=event.obj.from_id,
                              message=message,
                              random_id=get_random_id(), keyboard=keyboard)


def accept_movie(event, only, from_replace):
    only.countFindFilm = 0

    if from_replace:
        sec_only = ChatRoll(only.chat_id)
        sec_only.open_db()
    else:
        sec_only = search_chat(only.chat_id)[0]

    legitimacy = check_legitimacy(only.targetMovie, sec_only)

    if legitimacy:
        message = "&#10071; Этот фильм нелегитимен! &#10071;\n&#10071; Причина: " + legitimacy + ' &#10071;'
        session_api.messages.send(peer_id=event.obj.from_id,
                                  message=message,
                                  random_id=get_random_id())
        only.searchMovie = None
        only.targetMovie = None
        return

    only.set_movies()
    if from_replace:
        save_movies_to_db(only.chat_id, only.man_id, ";".join(only.movies))
        message = 'Текущий список фильмов: \n' + list_of_films(only.movies)
        session_api.messages.send(peer_id=event.obj.from_id,
                                  message=message,
                                  random_id=get_random_id())
        replace_movie.remove(only)
        return
    only.searchMovie = None
    only.targetMovie = None

    if len(only.movies) < 3:
        message = '&#128253; Записал этот фильм, жду следующего &#128253;'
    else:
        message = '&#9745; Принял от тебя все 3 фильма. &#9745;\n&#128253;&#128253;&#128253;\n' \
                  '&#10071; Тебе доступны команды &#10071;\n&#128172; ' \
                  '[ !заменить <(название,ID,номер фильма> ] &#128172;\n' \
                  '&#128172; [ !список ] &#128172;'
    session_api.messages.send(peer_id=event.obj.from_id,
                              message=message,
                              random_id=get_random_id())


def new_movie(event, only, keyboard, type_of_message):
    movie, message = name_to_id(event.obj.text, 0)
    if message != '0':
        if type_of_message == 0:
            only.search_movies(event.obj.text, movie)
    else:
        session_api.messages.send(peer_id=event.obj.from_id,
                                  message='&#9888; &#9888; &#9888;\n&#10071;'
                                          ' Не смог найти фильм по твоему запросу &#10071;\n'
                                          '&#129300; Наверняка у него другое название, попробуй еще &#129300;\n'
                                          '&#9888; &#9888; &#9888;\n',
                                  random_id=get_random_id())
        return
    if type_of_message == 0:
        message += 'Это он?&#129300; Отпиши + или -'
    else:
        message += '\n&#9889;' + search_url_movies(event.obj.text) + ' &#9889;'

    session_api.messages.send(peer_id=event.obj.from_id,
                              message=message,
                              random_id=get_random_id(), keyboard=keyboard)


# boolTuping = False
roll_movie = []
replace_movie = []


def main(event):
    if event.type == VkBotEventType.MESSAGE_NEW:

        if event.from_chat:
            again_plus = False
            try:
                if event.obj.action.get('type') == 'chat_invite_user':
                    if event.obj.action.get('member_id') < 0:
                        session_api.messages.send(chat_id=event.chat_id,
                                                  message='Привет, я kino-bot. &#9996;\n&#10071; Для того, чтобы '
                                                          'начать - необходимо назначить меня администратором.\n'
                                                          '&#128253;\nЯ помогу вам определится с выбором фильма.&#9762;\n'
                                                          'Для этого напишите &#128172; [ !фильм ] &#128172; в чат '
                                                          'и от тех, кто поставит &#128172; [ + ] &#128172; '
                                                          'я жду 3 фильма. После этого, командой &#128172; [ !ролл ]'
                                                          ' я выберу '
                                                          'случайный фильм &#11088; , а оставшиеся я скину '
                                                          'вам в лс, для дальнейшего использования.\n&#128253;\n'
                                                          '&#128161; Весь список доступных команд вы можете узнать '
                                                          'с помощью &#128172; [ !команды ] &#128172;',
                                                  random_id=get_random_id())
                    return
            except:
                pass

            if event.obj.text.lower() == '!команды':
                session_api.messages.send(chat_id=event.chat_id,
                                          message='Список команд:\n&#128172;&#128172;&#128172;\n'
                                                  '____________________________________________________________'
                                                  '___\n'
                                                  '&#128172; [ !фильм ] - запускает сбор фильмов\n'
                                                  '&#128172; [ + ] - подтверждает вашу готовность к выбору '
                                                  'случайного фильма.'
                                                  '&#10071; Работает только после написания команды &#128172; '
                                                  '[ !фильм ] &#128172;&#10071;\n'
                                                  '&#128172; [ !ролл ] - запуск выбора случайного фильма. '
                                                  '&#10071; Работает только после '
                                                  'написания команды &#128172; [ !фильм ] &#128172; и при '
                                                  'условии, что все, кто поставили '
                                                  '&#128172; [ + ] &#128172; скинули боту по 3 фильма &#10071;\n'
                                                  '&#128172; [ !команды ] - скидывает список доступных команд в чат\n'
                                                  '&#128172; &#128081; [ !исключить <(актера,жанр,страну)> '
                                                  '<значение> ] - исключает фильмы с указанным актером'
                                                  ' или жанром\n'
                                                  '&#128172; &#128081; [ !вернуть <(актера,жанр,страну)> '
                                                  '<значение> ] - позволяет смотреть фильмы с указанным'
                                                  ' актером, если он был когда либо исключен\n'
                                                  '&#128172; &#128081; [ !установить <(рейтинг,год,время)> '
                                                  '<Условие(>,<,>=,<=,=)> <значение> ] - позволяет '
                                                  ' ограничить сбор фильмов по указанным парамерам \n'
                                                  '&#128172; [ !стоп ] - останавливает сбор фильмов\n'
                                                  '&#10071; Команды со значком &#128081; доступны только '
                                                  'администраторам чата\n'
                                                  '_______________________________________________________________',
                                          random_id=get_random_id())
                return

            only, again_movies_roll = search_chat(event.chat_id)

            try:
                man = only.getMan()
                for j in range(len(only.man)):
                    if man[j].man_id == event.obj.from_id:
                        again_plus = True
            except:
                pass

            if event.obj.text.lower() == '!фильм':
                film(event, again_movies_roll)
                return

            elif event.obj.text.lower() == '+':
                ready_to_film(event, again_movies_roll, again_plus, only)
                return

            elif event.obj.text.lower() == '!ролл':
                chat_roll(event, again_movies_roll, only)
                return

            elif event.obj.text.lower() == '!стоп':
                stop(event, again_movies_roll, only)
                return

            elif event.obj.text.lower()[0:10] == '!исключить' or event.obj.text.lower()[0:8] == '!вернуть':
                del_ret(event)
                return

            elif event.obj.text.lower()[0:11] == '!установить':
                chat_set(event)
                return

        elif event.from_user:
            from_replace = None
            only, from_group = search_man(event.obj.from_id)

            if not from_group:
                only, from_replace = search_man_for_replace(event.obj.from_id)

            if from_group or from_replace:

                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('+', color=VkKeyboardColor.POSITIVE)
                keyboard.add_button('-', color=VkKeyboardColor.NEGATIVE)
                keyboard = keyboard.get_keyboard()

                if event.obj.text.lower()[0:9] == '!заменить':
                    replace(event, only)
                    return
                # except:
                #     break
                # if num > 3 or num < 1 or len(only.movies)<num:
                #     break
                # else:
                #     removie = only.Removie(num)
                #     message = 'Фильм &#128253; ' + removie.title + ' &#128253; был удален\n' \
                #                                              'Жду от тебя фильма на замену.'
                #     session_api.messages.send(peer_id=event.obj.from_id,
                #                               message=message,
                #                               random_id=get_random_id())

                elif event.obj.text.lower() == "!список":
                    chat_list(event, only)
                    return

                if len(only.movies) < 3:

                    if event.obj.text == '-' and only.searchMovie:
                        reject_movie(event, only, keyboard)
                        return

                    elif event.obj.text == '+' and only.searchMovie:
                        accept_movie(event, only, from_replace)
                        return

                    else:
                        new_movie(event, only, keyboard, 0)
                        return

                else:
                    message = '&#9745; Твои 3 фильма приняты, ожидай ролла! &#9745;'
                    session_api.messages.send(peer_id=event.obj.from_id,
                                              message=message,
                                              random_id=get_random_id())
                    return

            else:
                if event.obj.text.lower() == 'начать':
                    session_api.messages.send(peer_id=event.obj.from_id,
                                              message='Привет, я kino-bot. &#9996;\n&#128253; Скинь мне '
                                                      'название фильма, и '
                                                      'я напишу тебе информацию о нем. &#128253;',
                                              random_id=get_random_id())
                    return
                elif event.obj.text.lower()[0:3] == '!kp' or \
                        event.obj.text.lower()[0:3] == '!кп':
                    kp_id = int(event.obj.text[event.obj.text.find(" ") + 1:])
                    save_kp_id(event.obj.from_id, kp_id)
                    session_api.messages.send(peer_id=event.obj.from_id,
                                              message='Прикреплен kp_id ' + str(kp_id),
                                              random_id=get_random_id())
                elif event.obj.text.lower()[0:9] == '!заменить':
                    # replace_in_db(event)
                    return
                #
                #     movies=useDBForMovies(event.obj.from_id,None)
                #     if (movies):
                #         removie = None
                #         try:
                #             num = int(event.obj.text[10:])
                #             if num < 1: break #############
                #             if num < 4:
                #                 #if len(movies)>1: break ###############
                #                 try:
                #                     str = movies[0][0]
                #                     movienew = ""
                #                     for i in range (movies[0][0].count(';')):
                #                         if i != (num-1):
                #                             movienew += str[:str.find(';')+1]
                #                         else:
                #                             delmovie = str[:str.find(';')+1]
                #                         str = str[str.find(';')+1:]
                #                     a=10
                #                 except:
                #                     pass
                #             else:
                #                 a = 10
                #                 #for i in range(len(only.movies)):
                #                     #if only.movies[i].id == num:
                #                         #removie = only.movies.pop(i)
                #                         #break
                #         except:
                #             num = event.obj.text[10:]
                #             #for i in range(len(only.movies)):
                #                 #if only.movies[i].title.lower() == num.lower():
                #                     #removie = only.movies.pop(i)
                #             break
                #         if removie:
                #             message = 'Фильм &#128253; ' + removie.title + ' &#128253; был удален\n' \
                #                                                            'Жду от тебя фильма на замену.'
                #         else:
                #             message = '&#10071; Не удалось удалить фильм &#10071;'
                #         session_api.messages.send(peer_id=event.obj.from_id,
                #                                   message=message,
                #                                   random_id=get_random_id())
                #     else:
                #         break

                elif event.obj.text != '+' and event.obj.text != '-':
                    new_movie(event, None, None, 1)
                    return


def run():
    while True:
        for event in long_poll.listen():
            threading.Thread(target=main, args=(event,), daemon=True).start()


run()
