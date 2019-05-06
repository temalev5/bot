# -*- coding: utf-8 -*-
import threading
import time
import vk_api
import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard,VkKeyboardColor
from datetime import datetime
from vk_api.utils import get_random_id
from sm import NameToID
from sm import getName
import os
from lordfilm import SearchURLMovies


#login, password = "login", "password"
#vk_session = vk_api.VkApi(login, password)
#vk_session.auth()

token = os.environ.get('BOT_TOKEN')
vk_session = vk_api.VkApi(token=token)

session_api = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, '181453927')


def ChekAlreadyUse(man_id, chat_id):
    try:
        history = session_api.messages.getHistory(offset = 0, count = 25, user_id = man_id)
        for i in range(25):
            if history.get('items')[i].get('text')[0] == '$':
                term = history.get('items')[i].get('text').find('\n')
                message_chat_id = int(history.get('items')[i].get('text')[1:term])
                if chat_id == message_chat_id:
                    movies = history.get('items')[i].get('text').split('\n')
                    movies.pop(0)
                    break
        if len(movies) > 3:
            movies = movies[0:3]
        return movies
    except:
        movies = []
        return movies

    print(history)

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
        self.movies = []
        self.mc = 0
        self.searchMovie = '0'
        self.countFindFilm = 0
        self.targetMovie = '0'

    def getName(self):
        userinfo = session_api.users.get(user_ids=self.man_id)
        username = userinfo[0].get('first_name')
        return username

    def SearchMovies(self,movi):
        self.SearchMovie = getName(movi, self.countFindFilm)
        self.targetMovie = self.SearchMovie

    def TargetMovie(self,movi):
        self.targetMovie = getName(movi, self.countFindFilm)

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

    def newMan(self, chat_id, man_id):
        self.man.append(Man(chat_id, man_id))

    def newManm(self,chat_id,man_id, movies):
        self.man.append(Man(chat_id, man_id))
        self.man[len(man)-1].movies = movies

    def getMan(self):
        return self.man

    def SendFilmsToAll(self):
        for i in range(len(self.man)):
            message = '$' + str(self.chat_id) + '\n'
            for j in range(len(self.man[i].movies)):
                message += man[i].movies[j] + '\n'
            session_api.messages.send(peer_id=man[i].man_id,
                                      message=message,
                                      random_id=get_random_id())

    def roll(self):

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
                    filmlist += man[i].movies[j] + '\n'
                    listfilm.append(man[i].movies[j])
        filmlist += '***********************\n_______________________________________________________________\n'
        rnd = random.randint(0, len(listfilm)-1)
        removiemovie = listfilm[rnd]
        retlistfiml += NameToID(listfilm[rnd], 0)

        url = SearchURLMovies(removiemovie)

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
            print(u'Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
            print(u'Текст сообщения: ' + str(event.obj.text))

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
                    print('hello')


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
                                                      '&#128172; [ !команды ] - скидывает список доступных команд в чат.\n'
                                                      '&#128172; [ привет ] - hello\n'
                                                      '_______________________________________________________________',
                                              random_id=get_random_id())
                    break

                for i in range(len(rollMoive)):
                    if rollMoive[i].chat_id == event.chat_id:
                        only = rollMoive[i]
                        again_moviesroll = True
                try:
                    man = only.getMan()
                    for j in range(len(only.man)):
                        if man[j].man_id == event.obj.from_id:
                            again_plus = True
                except:
                    print('hello')

                if event.obj.text.lower() == '!фильм':
                    if again_moviesroll:
                        session_api.messages.send(chat_id=event.chat_id, message='Сбор фильмов уже начался!!',
                                                  random_id=get_random_id())
                        break
                    else:
                        rollMoive.append(ChatRoll(event))
                        session_api.messages.send(chat_id=event.chat_id, message='Все, кто готов смотреть + в чат', random_id=get_random_id())
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
                                if len(movies) == 0:

                                    keybord = VkKeyboard(one_time=True)
                                    #keybord.add_button('Ебу собак', color=VkKeyboardColor.PRIMARY)
                                    #keybord.add_line()
                                    #keybord.add_button('Не ебу собак', color=VkKeyboardColor.DEFAULT)
                                    #keybord.add_line()
                                    #keybord.add_button('Ебу детей', color=VkKeyboardColor.DEFAULT)
                                    keybord = keybord.get_keyboard()

                                    session_api.messages.send(peer_id = event.obj.from_id,
                                                        message='Скидывай назвние фильма сюда',
                                                        random_id=get_random_id(), keybord = keybord)
                                    only.newMan(event.chat_id, event.obj.from_id)
                                    break
                                elif len(movies) < 3:
                                    session_api.messages.send(peer_id=event.obj.from_id,
                                                              message='Принял от тебя ' + str(len(movies)) + ' фильма, жду еще ' + str((3 - len(movies))),
                                                              random_id=get_random_id())
                                    only.newManm(event.chat_id, event.obj.from_id, movies)
                                    break
                                else:
                                    session_api.messages.send(peer_id=event.obj.from_id,
                                                              message='&#9745; Принял от тебя все 3 фильма. &#9745;\n&#128253;&#128253;&#128253;\n' \
                                                                        '&#10071; Тебе доступна команда &#128172; [ !заменить <номер фильма> ] &#128172;',
                                                              random_id=get_random_id())
                                    only.newManm(event.chat_id, event.obj.from_id, movies)
                                    break

                                #only.newMan(event.chat_id, event.obj.from_id)
                                #ChekAlreadyUse(event.obj.from_id)
                            except:

                                userinfo = session_api.users.get(user_ids = event.obj.from_id)
                                username = userinfo[0].get('first_name')

                                message = '@id' + str(event.obj.from_id) + \
                                        ' (' + username + '), разреши мне писать тебе сообщения\n' \
                                                            'Для этого перейди в мою группу, кликнув на меня.\n' \
                                                            'Либо просто напиши мне первый'

                                session_api.messages.send(chat_id=event.chat_id, message= message ,
                                                    random_id=get_random_id())
                                break

                elif event.obj.text == '!ролл':
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
                        session_api.messages.send(chat_id=event.chat_id, message='Для начала необходимо прописать !фильм, '
                                                                                 'для того, чтобы запустить сбор фильмов.'
                                                                            ,
                                                  random_id=get_random_id())
                        break
                    #t.join()

            if event.from_user:
                man = []
                only = None
                from_group = False

                for i in range(len(rollMoive)):
                    man = rollMoive[i].getMan()
                    for j in range(len(rollMoive[i].man)):
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

                        if event.obj.text == '-':
                            #t = threading.Thread(target=Typing, args=(event.obj.from_id,))
                            #t.start()
                            behmovie = only.SearchMovie
                            only.countFindFilm += 1
                            message = NameToID(behmovie, only.countFindFilm)
                            if message != '0':
                                only.TargetMovie(behmovie)
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
                        elif event.obj.text == '+':
                            only.countFindFilm = 0
                            only.SetMovies()

                            #keybord = VkKeyboard(one_time=True)
                            #keybord.add_button('Изменить первый', color=VkKeyboardColor.PRIMARY)
                            #keybord.add_line()
                            #keybord.add_button('Изменить второй', color=VkKeyboardColor.DEFAULT)
                            #keybord.add_line()
                            #keybord.add_button('Изменить третий', color=VkKeyboardColor.DEFAULT)
                            #keybord = keybord.get_keyboard()

                            if len(only.movies) < 3:
                                message = 'Записал этот фильм, жду следующего'
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
                            message = NameToID(event.obj.text, 0)
                            if message != '0':
                                only.SearchMovies(event.obj.text)
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
                                message = 'Фильм &#128253; ' + removie + ' &#128253; был удален\n' \
                                                                         'Жду от тебя фильма на замену.'
                                session_api.messages.send(peer_id=event.obj.from_id,
                                                          message=message,
                                                          random_id=get_random_id())

                            #text = event.obj.text[12:len(event.obj.text)]
                        else:
                            message = 'Твои 3 фильма приняты, ожидай ролла!'
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
                        message = NameToID(event.obj.text, 0)
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
