# -*- coding: utf-8 -*-
from kinopoisk.movie import Movie


def getName(name, pos):
    movie_list = Movie.objects.search(name)
    if (len(movie_list) == 0) or (pos >= len(movie_list)):
        return '0'
    else:
        return movie_list[pos].title

def getNameByID(id):
    movie = Movie(id=id)
    movie.get_content('main_page')
    try:
        movie.genres.remove('... слова')
    except:
        print('hello')
    return movie



def movieToText(name):
    try:
        nametoid = name.title + ' | '
        nametoid += str(name.year) + ' | '
        nametoid += 'ID = ' + str(name.id) + ' | '

        for i in range(len(name.countries)):
            country = name.countries[i]
            if i < 2 and i < len(name.countries) - 1:
                nametoid += country + ', '
            elif i == 2 or i == len(name.countries) - 1:
                nametoid += country + '\n'
                break

        nametoid += name.tagline + '\n'
        nametoid += '_______________________________________________________________\n'
        nametoid += 'Актеры: '
        # nametoid = Coding(nametoid)

        for i in range(len(name.actors)):
            act = name.actors[i].name
            if i < 2 and i < len(name.actors) - 1:
                nametoid += act + ', '
            elif i == 2 or i == len(name.actors) - 1:
                nametoid += act + '\n'
                break

        nametoid += 'Жанры: '

        for i in range(len(name.genres)):
            gnr = name.genres[i]
            if i < 3 and i < len(name.genres) - 1:
                nametoid += gnr + ', '
            elif i == 3 or i == len(name.genres) - 1:
                nametoid += gnr + '\n'
                break

        nametoid += 'Рейтинг: ' + str(name.rating)

        if name.rating != None:

            if name.rating < 5.5:
                nametoid += '&#10060;\n'
            elif name.rating < 7.0:
                nametoid += '&#9888;\n'
            else:
                nametoid += '&#9989;\n'
        else:
            nametoid += '\n'

        nametoid += 'Время: ' + str(name.runtime) + 'мин\n'
        nametoid += '_______________________________________________________________\n'
        # nametoid += 'Это он?&#129300; Отпиши + или -'

        # print(movie_list[pos].title.encode('utf8'))
        print(name.plot)
        print(name.rating)
        return nametoid
    except:
        return '0'

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
                print('')

            nametoid = movieToText(movie_list[pos])

        return movie_list[pos],nametoid
    except:
        return '0','0'