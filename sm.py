# -*- coding: utf-8 -*-
from kinopoisk.movie import Movie
import codecs

def NameToID(name):
    movie_list = Movie.objects.search(name)
    if (len(movie_list) == 0):
        nametoid = 0
    else:
        movie_list[0].get_content('main_page')
        movie_list[0].get_content('cast')

        nametoid = movie_list[0].title + ' | '
        nametoid += str(movie_list[0].year) + ' | '
        nametoid += 'ID = ' + str(movie_list[0].id) + ' | '


        for i in range(len(movie_list[0].countries)):
            country = movie_list[0].countries[i]
            if i < 2 and i < len(movie_list[0].countries)-1:
                nametoid += country + ', '
            elif i == 2 or i == len(movie_list[0].countries)-1:
                nametoid += country + '\n'
                break

        nametoid += movie_list[0].tagline + '\n'
        nametoid += '_______________________________________________________________\n'
        nametoid += 'Актеры: '
        #nametoid = Coding(nametoid)

        for i in range(len(movie_list[0].actors)):
            act = movie_list[0].actors[i].name
            if i < 2 and i < len(movie_list[0].actors)-1:
                nametoid += act + ', '
            elif i == 2 or i == len(movie_list[0].actors) - 1:
                nametoid += act + '\n'
                break

        nametoid += 'Жанры: '

        for i in range(len(movie_list[0].genres)):
            gnr = movie_list[0].genres[i]
            if i < 3 and i < len(movie_list[0].genres)-1:
                nametoid += gnr + ', '
            elif i == 3 or i == len(movie_list[0].genres) - 1:
                nametoid += gnr + '\n'
                break

        nametoid += 'Рейтинг: ' + str(movie_list[0].rating)

        if movie_list[0].rating != None:

            if movie_list[0].rating < 5.5:
                nametoid += '&#10060;\n'
            elif movie_list[0].rating < 7.0:
                nametoid += '&#9888;\n'
            else:
                nametoid += '&#9989;\n'
        else:
            nametoid += '\n'

        nametoid += 'Время: ' + str(movie_list[0].runtime) + 'мин\n'
        nametoid += '_______________________________________________________________\n'
        nametoid += 'Это он?&#129300; Отпиши + или -'


        #print(movie_list[0].title.encode('utf8'))
        print(movie_list[0].plot)
        print(movie_list[0].rating)

    return nametoid