# -*- coding: utf-8 -*-
from kinopoisk.movie import Movie
# from main import ratingEmoji


def rating_emoji(rating):
    if rating:
        if rating < 5:
            return '&#10060;'
        elif rating < 7:
            return '&#9888;'
        elif rating <= 10:
            return '&#9989;'
    else:
        return ''


def get_name_by_id(movie_id):
    movie = Movie(id=movie_id)
    movie.get_content('main_page')
    try:
        movie.genres.remove('... слова')
    except:
        pass
    return movie


def movie_to_text(name):
    try:
        name_to_id = name.title + ' | '
        name_to_id += str(name.year) + ' | '
        name_to_id += 'ID = ' + str(name.id) + ' | '

        for i in range(len(name.countries)):
            country = name.countries[i]
            if i < 2 and i < len(name.countries) - 1:
                name_to_id += country + ', '
            elif i == 2 or i == len(name.countries) - 1:
                name_to_id += country + '\n'
                break

        name_to_id += name.tagline + '\n'
        name_to_id += '_______________________________________________________________\n'
        name_to_id += 'Актеры: '

        for i in range(len(name.actors)):
            act = name.actors[i].name
            if i < 2 and i < len(name.actors) - 1:
                name_to_id += act + ', '
            elif i == 2 or i == len(name.actors) - 1:
                name_to_id += act + '\n'
                break

        name_to_id += 'Жанры: '

        for i in range(len(name.genres)):
            gnr = name.genres[i]
            if i < 3 and i < len(name.genres) - 1:
                name_to_id += gnr + ', '
            elif i == 3 or i == len(name.genres) - 1:
                name_to_id += gnr + '\n'
                break

        name_to_id += 'Рейтинг: ' + str(name.rating)

        name_to_id += rating_emoji(name.rating) + '\n'
        #if name.rating != None:

        #    if name.rating < 5.5:
        #        nametoid += '&#10060;\n'
        #    elif name.rating < 7.0:
        #        nametoid += '&#9888;\n'
        #    else:
        #        nametoid += '&#9989;\n'
        #else:
        #    nametoid += '\n'

        name_to_id += 'Время: ' + str(name.runtime) + 'мин\n'
        name_to_id += '_______________________________________________________________\n'

        print(name.plot)
        print(name.rating)
        return name_to_id
    except:
        return '0'

def name_to_id(name, pos):
    try:
        movie_list = Movie.objects.search(name)
        if (len(movie_list) == 0) or (pos >= len(movie_list)):
            name_to_id = '0'
        else:
            movie_list[pos].get_content('main_page')
            #movie_list[pos].get_content('cast')
            try:
                movie_list[pos].genres.remove('... слова')
            except:
                pass

            name_to_id = movie_to_text(movie_list[pos])

        return movie_list[pos], name_to_id
    except:
        return '0','0'