# -*- coding: utf-8 -*-
from kinopoisk.movie import Movie
import codecs


def getName(name, pos):
    movie_list = Movie.objects.search(name)
    if (len(movie_list) == 0) or (pos >= len(movie_list)):
        return '0'
    else:
        return movie_list[pos].title

def NameToID(name, pos):
    try:
        movie_list = Movie.objects.search(name)
        if (len(movie_list) == 0) or (pos >= len(movie_list)):
            nametoid = '0'
        else:
            movie_list[pos].get_content('main_page')
            #movie_list[pos].get_content('cast')
            try:
                movie_list[pos].genres.remove('... слова')
            except:
                print('hello')


            nametoid = movie_list[pos].title + ' | '
            nametoid += str(movie_list[pos].year) + ' | '
            nametoid += 'ID = ' + str(movie_list[pos].id) + ' | '


            for i in range(len(movie_list[pos].countries)):
                country = movie_list[pos].countries[i]
                if i < 2 and i < len(movie_list[pos].countries)-1:
                    nametoid += country + ', '
                elif i == 2 or i == len(movie_list[pos].countries)-1:
                    nametoid += country + '\n'
                    break

            nametoid += movie_list[pos].tagline + '\n'
            nametoid += '_______________________________________________________________\n'
            nametoid += 'Актеры: '
            #nametoid = Coding(nametoid)

            for i in range(len(movie_list[pos].actors)):
                act = movie_list[pos].actors[i].name
                if i < 2 and i < len(movie_list[pos].actors)-1:
                    nametoid += act + ', '
                elif i == 2 or i == len(movie_list[pos].actors) - 1:
                    nametoid += act + '\n'
                    break

            nametoid += 'Жанры: '

            for i in range(len(movie_list[pos].genres)):
                gnr = movie_list[pos].genres[i]
                if i < 3 and i < len(movie_list[pos].genres)-1:
                    nametoid += gnr + ', '
                elif i == 3 or i == len(movie_list[pos].genres) - 1:
                    nametoid += gnr + '\n'
                    break

            nametoid += 'Рейтинг: ' + str(movie_list[pos].rating)

            if movie_list[pos].rating != None:

                if movie_list[pos].rating < 5.5:
                    nametoid += '&#10060;\n'
                elif movie_list[pos].rating < 7.0:
                    nametoid += '&#9888;\n'
                else:
                    nametoid += '&#9989;\n'
            else:
                nametoid += '\n'

            nametoid += 'Время: ' + str(movie_list[pos].runtime) + 'мин\n'
            nametoid += '_______________________________________________________________\n'
            #nametoid += 'Это он?&#129300; Отпиши + или -'


            #print(movie_list[pos].title.encode('utf8'))
            print(movie_list[pos].plot)
            print(movie_list[pos].rating)

        return nametoid
    except:
        return '0'