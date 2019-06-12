# -*- coding: utf-8 -*-
import threading
import time
import vk_api
import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard,VkKeyboardColor
from datetime import datetime
from db import useDB,useDBForMovies,saveBD,saveToBD,saveToBDset
from vk_api.utils import get_random_id
from sm import NameToID,movieToText,getName,getNameByID
import os
from lordfilm import SearchURLMovies


#login, password = "login", "password"
#vk_session = vk_api.VkApi(login, password)
#vk_session.auth()

token = os.environ.get('BOT_TOKEN')
vk_session = vk_api.VkApi(token=token)

session_api = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, '181453927')



def cheker(one,condition,two):

    if ((one) and (two)):
        if (condition == ">"):
            if (one > two):
                return "Нелегитимный"
        if (condition == ">="):
            if (one >= two):
                return "Нелегитимный"
        if (condition == "<"):
            if (one < two):
                return "Нелегитимный"
        if (condition == "<="):
            if (one <= two):
                return "Нелегитимный"
        if (condition == "="):
            if (one != two):
                return "Нелегитимный"

def chekLegitimacy(movie,chat):
    for i in range(len(chat.man)):
        for j in range (len(chat.man[i].movies)):
            if chat.man[i].movies[j].id == movie.id:
                return "Повторяющийся фильм"

    if (chat.ex_actors):
        ex_actors = chat.ex_actors.split(';')
        ex_actors.remove("")
        for i in range(len(ex_actors)):
            for j in range(len(movie.actors)):
                if (ex_actors[i].lower()==movie.actors[j].name.lower()):
                    return "Запрещенный актер &#128253; " + movie.actors[j].name+' &#128253;'

    if ((chat.ex_country) and (movie.countries)):
        ex_country = chat.ex_country.split(';')
        ex_country.remove("")
        for i in range(len(ex_country)):
            for j in range(len(movie.countries)):
                if (ex_country[i].lower()==movie.countries[j].lower()):
                    return "Запрещенная страна &#128253; " + movie.countries[j]+' &#128253;'


    if ((chat.ex_janre) and (movie.genres)):
        ex_janre = chat.ex_janre.split(';')
        ex_janre.remove("")
        for i in range(len(ex_janre)):
            for j in range(len(movie.genres)):
                if (ex_janre[i].lower()==movie.genres[j].lower()):
                    return "Запрещенный жанр &#128253; " + movie.genres[j]+' &#128253;'

    if (cheker(chat.ex_rating,chat.ex_rating_condition,movie.rating) == "Нелегитимный"): return "Не подходит по рейтингу &#11088; "+ str(movie.rating) + " &#11088;"
    if (cheker(chat.ex_time,chat.ex_time_condition,movie.runtime) == "Нелегитимный"): return "Не подходит по времени &#11088; " + str(movie.runtime) + " &#11088;"
    if (cheker(chat.ex_year, chat.ex_year_condition, movie.year) == "Нелегитимный"): return "Не подходит по году создания &#11088; " + str(movie.year) + " &#11088;"


def searchMan(rollMoive):
    man = []
    try:
        for i in range(len(rollMoive)):
            man = rollMoive[i].getMan()
        return man
    except:
        searchMan(rollMoive)


def searchChat(rollMoive,id):
    only = []
    again_moviesroll = False
    try:
        for i in range(len(rollMoive)):
            if rollMoive[i].chat_id == id:
                only = rollMoive[i]
                again_moviesroll = True
        return only,again_moviesroll
    except:
        searchChat(rollMoive,id)

def RemoveRollMovie(i,this, chat_id):
    time.sleep(1800)
    if (rollMoive.count(this)>0):
        this.SendFilmsToAll()
        session_api.messages.send(chat_id=chat_id, message='&#9888; &#9888; &#9888;\n&#10071;'
                                                       ' Сбор фильмов был остановлен. &#10071;\n&#10071;'
                                                       ' Время сбора фильмов вышло. &#10071;\n'
                                                       '&#9888; &#9888; &#9888;',
                                random_id=get_random_id())
        rollMoive.remove(this)


def ChekAlreadyUse(man_id, chat_id):
    movies = useDBForMovies(man_id,chat_id)
    movie = []
    if (movies):
        movies = movies[0][0]
        movies = movies.split(';')
        movies.remove("")
        if (len(movies)<=3):
            for i in range(len(movies)):
                movie.append(getNameByID(movies[i][movies[i].find("(") + 1:movies[i].find(")")]))
            if len(movie) > 3:
                movie = movie[0:3]
            return movie
    else:
        return movie


    #try:
    #    history = session_api.messages.getHistory(offset = 0, count = 25, user_id = man_id)
    #    for i in range(25):
    #        if history.get('items')[i].get('text')[0] == '$':
    #           term = history.get('items')[i].get('text').find('\n')
    #            message_chat_id = int(history.get('items')[i].get('text')[1:term])
    #            if chat_id == message_chat_id:
    #                movies = history.get('items')[i].get('text').split('\n')
    #                movies.pop(0)
    #                break
    #    movie = []
    #    for i in range(len(movies)):
    #        movie.append(getNameByID(movies[i][movies[i].find("(")+1:movies[i].find(")")]))
    #    if len(movie) > 3:
    #        movie = movie[0:3]
    #    return movie
    #except:
    #    movies = []
    #    return movies

#def Typing(user_id):
    #boolTuping = True
    #while boolTuping:
        #print('успел')
        #session_api.messages.setActivity(peer_id=user_id,type = 'typing')
        #time.sleep(5)




class Man:

    def __init__(self, chat_id,man_id):
        self.chat_id = chat_id
        self.man_id = man_id
        self.ex_movies = []
        self.movies = []
        self.mc = 0
        self.searchMovie = None
        self.countFindFilm = 0
        self.targetMovie = None

    def getName(self):
        userinfo = session_api.users.get(user_ids=self.man_id)
        username = userinfo[0].get('first_name')
        return username

    def SearchMovies(self,movi,movie):
        self.searchMovie = getName(movi, self.countFindFilm)
        self.targetMovie = movie

    def TargetMovie(self,movi):
        self.targetMovie = movi

    def SetMovies(self):
        self.movies.append(self.targetMovie)

    def RemovieMovie(self):
        self.movies.pop()
        self.countFindFilm += 1

    def Removie(self,pos):
        return self.movies.pop(pos-1)


class ChatRoll:

    def __init__(self, event):
        self.chat_id = event.chat_id
        self.man = []
        self.ex_rating = None
        self.ex_rating_condition = ">"
        self.ex_janre = None
        self.ex_year = None
        self.ex_year_condition = ">"
        self.ex_time = None
        self.ex_time_condition = "<"
        self.ex_actors = None
        self.ex_country = None

    def openBD(self):
        result = useDB(self.chat_id)
        if (result):
            self.ex_rating = result[0][0]
            if (result[0][1]): self.ex_rating_condition = result[0][1]
            self.ex_janre = result[0][2]
            self.ex_year = result[0][3]
            if (result[0][4]): self.ex_year_condition = result[0][4]
            self.ex_time = result[0][5]
            if (result[0][6]): self.ex_time_condition = result[0][6]
            self.ex_actors = result[0][7]
            self.ex_country = result[0][8]

    def newMan(self, chat_id, man_id):
        self.man.append(Man(chat_id, man_id))
        print('Создал нового персонажа без фильмов' + str(man_id))

    def newManm(self,chat_id,man_id, movies):
        self.man.append(Man(chat_id, man_id))
        self.man[len(man)-1].movies = movies
        print('Создал нового персонажа ' + str(man_id) + str(movies))

    def getMan(self):
        return self.man

    def SendFilmsToAll(self):
        for i in range(len(self.man)):
            message = 'Список фильмов: \n'
            for j in range(len(self.man[i].movies)):
                if (j == 0):
                    message += '1&#8419; '
                elif (j == 1):
                    message += '2&#8419; '
                elif (j == 2):
                    message += '3&#8419; '
                message += self.man[i].movies[j].title + "(" + str(self.man[i].movies[j].id) + ') '
                if (self.man[i].movies[j].rating < 5):
                    message += '&#10060;\n'
                elif (self.man[i].movies[j].rating < 7):
                    message += '&#9888;\n'
                elif (self.man[i].movies[j].rating <= 10):
                    message += '&#9989;\n'
                else:
                    message += '\n'
                #message += man[i].movies[j].title + "("+str(man[i].movies[j].id)+")" + '\n'
            if (len(self.man[i].movies)!=0):
                session_api.messages.send(peer_id=man[i].man_id,
                                        message=message,
                                        random_id=get_random_id())
        saveBD(self)

    def roll(self):
        for i in range(len(self.man)):
            print(str(self.man[i].man_id) + str(self.man[i].movies))

        if len(self.man) == 0:
            return '0','0'

        filmlist = 'Список фильмов\n_______________________________________________________________\n'
        retlistfiml = 'СЛУЧАЙНЫЙ ФИЛЬМ:\n&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;' \
                      '&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;&#128293;' \
                      '&#128293;&#128293;\n '
        listfilm = []
        for i in range(len(self.man)):
            filmlist += '***********************\n* ' + man[i].getName() + ' *\n'
            if len(self.man[i].movies) < 3:
                return '0','0'
            elif len(self.man[i].movies) == 3:
                for j in range(len(self.man[i].movies)):
                    filmlist += man[i].movies[j].title + '\n'
                    listfilm.append(man[i].movies[j])
        filmlist += '***********************\n_______________________________________________________________\n'
        rnd = random.randint(0, len(listfilm)-1)
        removiemovie = listfilm[rnd]
        retlistfiml += movieToText(removiemovie)

        url = SearchURLMovies(removiemovie.title)

        retlistfiml += '\n&#9889;' + url + ' &#9889;'

        for i in range(len(self.man)):
            try:
                man[i].movies.remove(removiemovie)
            except:
                print()


        return filmlist, retlistfiml


boolTuping = False
k=0
rollMoive = []

while True:
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            again_moviesroll = False
            again_plus = False
            #print(u'Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
            #print(u'Текст сообщения: ' + str(event.obj.text))

            if event.from_chat:
                try:
                    if event.obj.action.get('type') == 'chat_invite_user':
                        session_api.messages.send(chat_id=event.chat_id,
                                                  message='Привет, я kino-bot. &#9996;\n&#10071; Для того, чтобы '
                                                          'начать - необходимо назначить меня администратором.\n'
                                                          '&#128253;\nЯ помогу вам определится с выбором фильма.&#9762;\n'
                                                          'Для этого напишите &#128172; [ !фильм ] &#128172; в чат '
                                                          'и от тех, кто поставит &#128172; [ + ] &#128172; '
                                                          'я жду 3 фильма. После этого, командой &#128172; [ !ролл ] я выберу '
                                                          'случайный фильм &#11088; , а оставшиеся я скину '
                                                          'вам в лс, для дальнейшего использования.\n&#128253;\n'
                                                          '&#128161; Весь список доступных команд вы можете узнать с помощью &#128172; [ !команды ] &#128172;',
                                                random_id=get_random_id())
                        break
                except:
                    print('')


                if event.obj.text.lower() == '!команды':
                    session_api.messages.send(chat_id=event.chat_id,
                                              message='Список команд:\n&#128172;&#128172;&#128172;\n'
                                                      '_______________________________________________________________\n'
                                                      '&#128172; [ !фильм ] - запускает сбор фильмов\n'
                                                      '&#128172; [ + ] - подтверждает вашу готовность к выбору случайного фильма.'
                                                      '&#10071; Работает только после написания команды &#128172; [ !фильм ] &#128172;&#10071;\n'
                                                      '&#128172; [ !ролл ] - запуск выбора случайного фильма. &#10071; Работает только после '
                                                      'написания команды &#128172; [ !фильм ] &#128172; и при условии, что все, кто поставили '
                                                      '&#128172; [ + ] &#128172; скинули боту по 3 фильма &#10071;\n'
                                                      '&#128172; [ !команды ] - скидывает список доступных команд в чат\n'
                                                      '&#128172; &#128081; [ !исключить <(актера,жанр,страну)> <значение> ] - исключает фильмы с указанным актером'
                                                      ' или жанром\n'
                                                      '&#128172; &#128081; [ !вернуть <(актера,жанр,страну)> <значение> ] - позволяет смотреть фильмы с указанным'
                                                      ' актером, если он был когда либо исключен\n'
                                                      '&#128172; &#128081; [ !установить <(рейтинг,год,время)> <Условие(>,<,>=,<=,=)> <значение> ] - позволяет '
                                                      ' ограничить сбор фильмов по указанным парамерам \n'
                                                      '&#128172; [ !стоп ] - останавливает сбор фильмов\n'
                                                      '&#10071; Команды со значком &#128081; доступны только администраторам чата\n'
                                                      '_______________________________________________________________',
                                              random_id=get_random_id())
                    break

                only,again_moviesroll = searchChat(rollMoive,event.chat_id)

                try:
                    man = only.getMan()
                    for j in range(len(only.man)):
                        if man[j].man_id == event.obj.from_id:
                            again_plus = True
                except:
                    print('')

                if event.obj.text.lower() == '!фильм':
                    if again_moviesroll:
                        session_api.messages.send(chat_id=event.chat_id, message='&#10071; Сбор фильмов уже начался &#10071;',
                                                  random_id=get_random_id())
                        break
                    else:
                        rollMoive.append(ChatRoll(event))
                        thRM = rollMoive[len(rollMoive)-1]
                        thRM.openBD()
                        threading.Thread(target=RemoveRollMovie, args=(0,thRM, event.chat_id),daemon=True).start()
                        message = "&#9888; Начался сбор фильмов &#9888;\n"
                        if ((thRM.ex_actors) or (thRM.ex_country) or (thRM.ex_janre) or (thRM.ex_rating) or (thRM.ex_time) or (thRM.ex_year)):
                            message += "&#10071; Параметры сбора :\n_______________________________\n"
                            if (thRM.ex_actors):
                                message += "&#128204; Исключенные актеры: &#128253; "+thRM.ex_actors.replace(';',' &#128253; ')+"\n"
                            if (thRM.ex_country):
                                message += "&#128204; Исключенные страны: &#128253; " + thRM.ex_country.replace(';',' &#128253; ')+"\n"
                            if (thRM.ex_janre):
                                message += "&#128204; Исключенные жанры: &#128253; " + thRM.ex_janre.replace(';',
                                                                                                                ' &#128253; ') + "\n"
                            if (thRM.ex_rating):
                                message += "&#128204; Рейтинг "+thRM.ex_rating_condition+" &#11088; " + str(thRM.ex_rating) + " &#11088;\n"
                            if (thRM.ex_time):
                                message += "&#128204; Время " + thRM.ex_time_condition + " &#11088; " + str(thRM.ex_time) + " &#11088;\n"
                            if (thRM.ex_year):
                                message += "&#128204; Год " + thRM.ex_year_condition + " &#11088; " + str(thRM.ex_year) + " &#11088;\n"
                            message += "_______________________________\n"
                        message += "&#10071; Поставь &#128172; [ + ] &#128172; в чат, если готов смотреть &#10071;"
                        print('Создал новый класс')
                        session_api.messages.send(chat_id=event.chat_id, message=message, random_id=get_random_id())

                        chat_title = session_api.messages.getConversationsById(peer_ids=event.chat_id + 2000000000)
                        chat_title = chat_title.get('items')[0].get('chat_settings').get('title')
                        chat_info = session_api.messages.getConversationMembers(peer_id=event.chat_id + 2000000000)
                        for i in range(len(chat_info.get('profiles'))):
                            id = chat_info.get('profiles')[i].get('id')
                            try:
                                session_api.messages.send(peer_id=id,
                                                        message= '&#9888; &#9888; &#9888;\n&#128253; '
                                                                 'В бесседе &#128173; ' + chat_title + ' &#128173; '
                                                                 'начался сбор фильмов, скорее ставь &#128172; [ + ] &#128172;'
                                                                 ', чтобы присоединится. &#128253;\n&#9888; &#9888; &#9888;',
                                                        random_id=get_random_id())
                            except:
                                print('Не смог отписать' + str(id))

                        break

                elif event.obj.text.lower() == 'привет':

                    #keybord1 = VkKeyboard()
                    #keybord = keybord.get_keyboard()

                    #keybord = {
                    #    "buttons":[],
                    #    "one_time":True
                    #}
                    #keybord = keybord.get_keyboard()
                    #keybord = keybord.get_empty_keyboard()

                    #session_api.messages.send(peer_id=event.obj.from_id,
                    #                          message='Скидывай назвние фильма сюда',
                    #                          random_id=get_random_id(), keybord=keybord1.get_empty_keyboard())




                    #session_api.messages.send(chat_id=event.chat_id, message='Hello', random_id=get_random_id())
                    break

                elif event.obj.text.lower() == '+':
                    if again_plus:
                        userinfo = session_api.users.get(user_ids=event.obj.from_id)
                        username = userinfo[0].get('first_name')

                        message = '@id' + str(event.obj.from_id) + ' (' + username + '), уже отписал тебе в лс'


                        session_api.messages.send(chat_id=event.chat_id, message=message,
                                                  random_id=get_random_id())
                        break
                    else:
                        if again_moviesroll:

                            try:
                                movies = []
                                movies = ChekAlreadyUse(event.obj.from_id, event.chat_id)
                                print('Принял от ' + str(event.obj.from_id) + str(movies))
                                if len(movies) == 0:

                                    session_api.messages.send(peer_id = event.obj.from_id,
                                                        message='&#128071; Скидывай название первого фильма сюда &#128071;',
                                                        random_id=get_random_id())
                                    only.newMan(event.chat_id, event.obj.from_id)
                                    print('Создал нового персонажа' + str(event.obj.from_id))
                                    break
                                elif len(movies) <= 3:
                                    message = 'Принял от тебя :\n'
                                    for i in range(len(movies)):
                                        if (i == 0):
                                            message += '1&#8419; '
                                        elif (i == 1):
                                            message += '2&#8419; '
                                        elif (i == 2):
                                            message += '3&#8419; '
                                        message += movies[i].title + "("+str(movies[i].id)+') '
                                        if (movies[i].rating<5):
                                            message += '&#10060;\n'
                                        elif (movies[i].rating<7):
                                            message += '&#9888;\n'
                                        elif (movies[i].rating<=10):
                                            message += '&#9989;\n'
                                        else:
                                            message += '\n'
                                    if len(movies)<3:
                                        message += '_____________________________\nЖду еще '+str((3 - len(movies)))+' &#128253;'
                                    else:
                                        message += '_____________________________\n&#9745; Принял от тебя все 3 фильма. &#9745;\n&#128253;&#128253;&#128253;\n' \
                                                                        '&#10071; Тебе доступна команда &#128172; [ !заменить <номер фильма> ] &#128172;'
                                    session_api.messages.send(peer_id=event.obj.from_id,
                                                              message=message,
                                                              random_id=get_random_id())
                                    only.newManm(event.chat_id, event.obj.from_id, movies)
                                    print('Создал нового персонажа' + str(event.obj.from_id) + str(movies))
                                    break

                                #only.newMan(event.chat_id, event.obj.from_id)
                                #ChekAlreadyUse(event.obj.from_id)
                            except:
#
                                userinfo = session_api.users.get(user_ids = event.obj.from_id)
                                username = userinfo[0].get('first_name')

                                message = '&#10071; @id' + str(event.obj.from_id) + \
                                        ' (' + username + '), разреши мне писать тебе сообщения\n' \
                                                            '&#128495; Для этого перейди в мою группу, кликнув на меня.\n' \
                                                            '&#128495; Либо просто напиши мне первый &#10071;'

                                session_api.messages.send(chat_id=event.chat_id, message= message ,
                                                  random_id=get_random_id())
                                break

                elif event.obj.text.lower() == '!ролл':
                    #t = threading.Thread(target=Typing, args=(event.chat_id,))
                    #t.start()
                    if again_moviesroll:
                        filmlist,listfilm = only.roll()
                        if filmlist != '0' and listfilm !='0':
                            session_api.messages.send(chat_id=event.chat_id, message=filmlist,
                                                  random_id=get_random_id())

                        #listfilm += NameToID(behmovie, 0)

                            session_api.messages.send(chat_id=event.chat_id, message=listfilm,
                                                  random_id=get_random_id())


                            only.SendFilmsToAll()
                            rollMoive.remove(only)
                            break
                    else:
                        session_api.messages.send(chat_id=event.chat_id, message='&#10071; Для начала необходимо прописать &#128172; [ !фильм ] &#128172; '
                                                                                 'для того, чтобы запустить сбор фильмов.'
                                                                            ,
                                                  random_id=get_random_id())
                        break
                elif event.obj.text.lower() == '!стоп':
                    if again_moviesroll:
                        only.SendFilmsToAll()
                        rollMoive.remove(only)
                        session_api.messages.send(chat_id=event.chat_id,
                                                  message='&#10071; Сбор фильмов остановлен &#10071;',
                                                  random_id=get_random_id())

                elif (event.obj.text.lower()[0:10] == '!исключить' or event.obj.text.lower()[0:8]=='!вернуть'):
                    t = event.obj.text[:event.obj.text.find(' ')]
                    items = session_api.messages.getConversationMembers(peer_id = 2000000000+event.chat_id).get('items')
                    for item in items:
                        if (item.get('member_id') == event.obj.from_id):
                            if (item.get('is_admin')):
                                name = event.obj.text[event.obj.text.find(' ') + 1:]
                                name = name[:name.find(' ')].lower()
                                if (name == "актера") or (name == "жанр") or (name == "страну"):
                                    value = event.obj.text[event.obj.text.find(' ') + 1:]
                                    value = value[value.find(' ') + 1:]+";"
                                    validate = saveToBD(event.chat_id,name,value.lower(),t)
                                    if validate==False:
                                        break
                                    message = ""
                                    what = "Исключен"
                                    whats = "доступен"
                                    if (name == "актера"): name = "актер"
                                    if (name == "страну"):
                                        name = "страна"
                                        what = "Исключена"
                                        whats = "доступна"
                                    if (t=="!исключить"):
                                        message = "&#128204; "+ what + " " + name + ' &#128253; ' + value[:-1] + ' &#128253;'
                                        a = 10
                                    elif (t=="!вернуть"):
                                        message = "&#128204; " + name + ' &#128253; ' + value[:-1] + " &#128253; теперь "+ whats + " &#9989;"

                                    session_api.messages.send(chat_id=event.chat_id,
                                                              message=message,
                                                              random_id=get_random_id())



                elif (event.obj.text.lower()[0:11] == '!установить'):
                    items = session_api.messages.getConversationMembers(peer_id=2000000000 + event.chat_id).get('items')
                    for item in items:
                        if (item.get('member_id') == event.obj.from_id):
                            if (item.get('is_admin')):
                                name = event.obj.text[event.obj.text.find(' ') + 1:]
                                name = name[:name.find(' ')].lower()
                                if (name == "рейтинг") or (name == "время") or (name == "год"):
                                    condition = event.obj.text[event.obj.text.find(' ') + 1:]
                                    condition = condition[condition.find(' ') + 1:]
                                    condition = condition[:condition.find(' ')]
                                    if (condition == ">") or (condition == "<") or (condition == ">=") or (condition == "<=") or (condition == "="):
                                        value = event.obj.text[event.obj.text.find(' ') + 1:]
                                        value = value[value.find(' ') + 1:]
                                        value = value[value.find(' ')+1:]
                                        saveToBDset(event.chat_id,name,condition,value)
                                        message = "&#128204; Установлен параметр &#128253; "+ name + " " + "фильма &#128253; " + condition + " &#11088;" + value + " &#11088;"
                                        session_api.messages.send(chat_id=event.chat_id,
                                                                  message=message,
                                                                  random_id=get_random_id())




            if event.from_user:
                man = []
                only = None
                from_group = False

                man = searchMan(rollMoive)
                for j in range(len(man)):
                    if man[j].man_id == event.obj.from_id:
                        only = man[j]
                        from_group = True

                #keybord = None

                if from_group:

                    keybord = VkKeyboard(one_time=True)
                    keybord.add_button('+', color=VkKeyboardColor.POSITIVE)
                    #keybord.add_line()
                    keybord.add_button('-', color=VkKeyboardColor.NEGATIVE)
                    #keybord.add_line()
                    #keybord.add_button('Изменить третий', color=VkKeyboardColor.DEFAULT)
                    keybord = keybord.get_keyboard()

                    if len(only.movies) < 3:

                        if ((event.obj.text == '-') and (only.searchMovie)):
                            #t = threading.Thread(target=Typing, args=(event.obj.from_id,))
                            #t.start()
                            behmovie = only.searchMovie
                            only.countFindFilm += 1
                            movie, message = NameToID(behmovie, only.countFindFilm)
                            if message != '0':
                                only.TargetMovie(movie)
                            else:
                                only.countFindFilm = 0
                                session_api.messages.send(peer_id=event.obj.from_id,
                                                          message='&#9888; &#9888; &#9888;\n&#10071;'
                                                                  ' Не смог найти фильм по твоему запросу &#10071;\n'
                                                                  '&#129300; Наверняка у него другое название, попробуй еще &#129300;\n'
                                                                  '&#9888; &#9888; &#9888;\n',
                                                          random_id=get_random_id())
                                break
                            message += 'Это он?&#129300; Отпиши + или -'

                            session_api.messages.send(peer_id=event.obj.from_id,
                                                      message=message,
                                                      random_id=get_random_id(), keyboard=keybord)
                            break
                            #t.join()
                        elif ((event.obj.text == '+') and (only.searchMovie)):
                            only.countFindFilm = 0

                            seconly = searchChat(rollMoive, only.chat_id)[0]

                            legetimacy = chekLegitimacy(only.targetMovie,seconly)

                            if (legetimacy):
                                message = "&#10071; Этот фильм нелегитимен! &#10071;\n&#10071; Причина: "+ legetimacy + ' &#10071;'
                                session_api.messages.send(peer_id=event.obj.from_id,
                                                          message=message,
                                                          random_id=get_random_id())
                                break

                            only.SetMovies()
                            only.searchMovie = None
                            only.targetMovie = None

                            #keybord = VkKeyboard(one_time=True)
                            #keybord.add_button('Изменить первый', color=VkKeyboardColor.PRIMARY)
                            #keybord.add_line()
                            #keybord.add_button('Изменить второй', color=VkKeyboardColor.DEFAULT)
                            #keybord.add_line()
                            #keybord.add_button('Изменить третий', color=VkKeyboardColor.DEFAULT)
                            #keybord = keybord.get_keyboard()

                            if len(only.movies) < 3:
                                message = '&#128253; Записал этот фильм, жду следующего &#128253;'
                            else:
                                message = '&#9745; Принял от тебя все 3 фильма. &#9745;\n&#128253;&#128253;&#128253;\n' \
                                          '&#10071; Тебе доступна команда &#128172; [ !заменить <номер фильма> ] &#128172;'

                            session_api.messages.send(peer_id=event.obj.from_id,
                                                      message=message,
                                                      random_id=get_random_id())
                            break


                        else:
                            #t = threading.Thread(target=Typing, args=(event.obj.from_id,))
                            #t.start()
                            movie,message = NameToID(event.obj.text, 0)
                            if message != '0':
                                only.SearchMovies(event.obj.text,movie)
                            else:
                                session_api.messages.send(peer_id=event.obj.from_id,
                                                          message='&#9888; &#9888; &#9888;\n&#10071;'
                                                                  ' Не смог найти фильм по твоему запросу &#10071;\n'
                                                                  '&#129300; Наверняка у него другое название, попробуй еще &#129300;\n'
                                                                  '&#9888; &#9888; &#9888;\n',
                                                          random_id=get_random_id())
                                break
                            message += 'Это он?&#129300; Отпиши + или -'

                            session_api.messages.send(peer_id=event.obj.from_id,
                                                      message=message,
                                                      random_id=get_random_id(), keyboard=keybord)
                            break
                            #t.join()

                    else:
                        if event.obj.text.lower()[0:9] == '!заменить':
                            try:
                                num = int(event.obj.text[10])
                            except:
                                break
                            if num > 3 or num < 1 or len(only.movies)<num:
                                break
                            else:
                                removie = only.Removie(num)
                                message = 'Фильм &#128253; ' + removie.title + ' &#128253; был удален\n' \
                                                                         'Жду от тебя фильма на замену.'
                                session_api.messages.send(peer_id=event.obj.from_id,
                                                          message=message,
                                                          random_id=get_random_id())

                            #text = event.obj.text[12:len(event.obj.text)]
                        else:
                            message = '&#9745; Твои 3 фильма приняты, ожидай ролла! &#9745;'
                            session_api.messages.send(peer_id=event.obj.from_id,
                                                message=message,
                                                random_id=get_random_id())
                            break


                else:
                    #t = threading.Thread(target=Typing, args=(event.obj.from_id,))
                    #t.start()
                    if event.obj.text.lower() == 'начать':
                        session_api.messages.send(peer_id=event.obj.from_id,
                                                  message='Привет, я kino-bot. &#9996;\n&#128253; Скинь мне название фильма, и ' 
                                                          'я напишу тебе информацию о нем. &#128253;',
                                                  random_id=get_random_id())
                        break

                    if event.obj.text != '+' and event.obj.text != '-':
                        movie,message = NameToID(event.obj.text, 0)
                        if message == '0':
                            session_api.messages.send(peer_id=event.obj.from_id,
                                                      message='&#9888; &#9888; &#9888;\n&#10071;'
                                                              ' Не смог найти фильм по твоему запросу &#10071;\n'
                                                              '&#129300; Наверняка у него другое название, попробуй еще &#129300;\n'
                                                              '&#9888; &#9888; &#9888;\n',
                                                      random_id=get_random_id())
                            break
                        message += '\n&#9889;' + SearchURLMovies(event.obj.text) + ' &#9889;'

                        session_api.messages.send(peer_id=event.obj.from_id,
                                              message=message,
                                              random_id=get_random_id())
                        break
                    #print('не успео')
                    #boolTuping = False
                    #t.join()
