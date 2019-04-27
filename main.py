# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard,VkKeyboardColor
from datetime import datetime
from vk_api.utils import get_random_id
from sm import NameToID

#login, password = "login", "password"
#vk_session = vk_api.VkApi(login, password)
#vk_session.auth()

token = "15886843296d1809121b5d9cdf1dec2e8ac75688f33c01f51d3b838f17707f7cf1a1e08d5c3225191b8b5"
vk_session = vk_api.VkApi(token=token)

session_api = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, '181453927')

#def MovieMaker()

class Man:

    def __init__(self, chat_id,man_id):
        self.chat_id = chat_id
        self.man_id = man_id
        self.movies = []
        self.mc = 0

    def SetMovies(self,movi):
        self.movies.append(movi)
        print(movi)




class ChatRoll:
    #countMan=0

    def __init__(self, event):
        self.chat_id = event.chat_id
        self.z = 0
        self.man = []

    def newMan(self, chat_id, man_id):
        self.man.append(Man(chat_id, man_id))
        self.z=+1
        #ChatRoll.countMan=+1

    def getMan(self):
        return self.man

    def getCountMan(self):
        return self.z


k=0
rollMoive = []

while True:
    again = False
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            print(u'Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
            print(u'Текст сообщения: ' + str(event.obj.text))
            if event.from_chat:
                for i in range(k):
                    if rollMoive[i].chat_id == event.chat_id:
                        again = True
                        session_api.messages.send(chat_id=event.chat_id, message='Сбор фильмов уже начался!!',
                                                  random_id=get_random_id())
                if event.obj.text.lower() == '!фильм' and (not again):
                    rollMoive.append(ChatRoll(event))
                    k+=1
                    session_api.messages.send(chat_id=event.chat_id, message='Все, кто готов смотреть + в чат', random_id=get_random_id())
                if event.obj.text.lower() == 'привет':
                    session_api.messages.send(chat_id=event.chat_id, message='Hello', random_id=get_random_id())

                if event.obj.text.lower() == '+':
                    for i in range(k):
                        if rollMoive[i].chat_id == event.chat_id:
                            rollMoive[i].newMan(event.chat_id, event.obj.from_id)
                    try:
                        session_api.messages.send(peer_id = event.obj.from_id,
                                              message='Скидывай назвние фильма сюда, либо его id на кинопоиске',
                                              random_id=get_random_id())
                    except:
                        userinfo = session_api.users.get(user_ids = event.obj.from_id)
                        username = userinfo[0].get('first_name')
                        #print (b)

                        message = '@id' + str(event.obj.from_id) + ' (' + username + '), разреши мне писать тебе сообщения\nДля этого перейди в мою группу, кликнув на меня.\nЛибо просто напиши мне первый'


                            #'Не могу отправить сообщение, @id' + str(event.obj.from_id) + ' (' + username + '), ' \
                             #       'напиши мне первый, а потом еще раз поставь + в чат.\n' \
                             #       'Либо разреши мне писать тебе сообщения&#128521'

                        session_api.messages.send(chat_id=event.chat_id, message= message ,
                                                 random_id=get_random_id())
            if event.from_user:
                if event.obj.text != '+' or event.obj.text != '-':
                    man = []
                    for i in range(k):
                        man = rollMoive[i].getMan()
                        for j in range(rollMoive[i].getCountMan()):
                            if man[j].man_id == event.obj.from_id:
                                keybord = VkKeyboard(one_time=True)
                                keybord.add_button('+', color= VkKeyboardColor.DEFAULT)
                                session_api.messages.send(peer_id=event.obj.from_id,
                                                      message=NameToID(event.obj.text),
                                                      random_id=get_random_id(),keyboard=keybord)

                            #man[j].SetMovies(event.obj.text)
                    keybord = VkKeyboard(one_time=True)
                    keybord.add_button('+', color=VkKeyboardColor.POSITIVE)
                    keybord.add_button('-', color=VkKeyboardColor.NEGATIVE)
                    keybord = keybord.get_keyboard()

                    session_api.messages.send(peer_id=event.obj.from_id,
                                                      message=NameToID(event.obj.text),
                                                      random_id=get_random_id(),keyboard = keybord)
