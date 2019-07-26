import psycopg2
import os

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


def save_to_db_set(chat_id, name, condition, value):
    cursor = conn.cursor()
    value_condition = condition
    if name == "рейтинг":
        name = "ex_rating"
        condition = "ex_rating_condition"
    if name == "время":
        name = "ex_time"
        condition = "ex_time_condition"
    if name == "год":
        name = "ex_year"
        condition = "ex_year_condition"

    cursor.execute('SELECT chats.' + name + ' FROM chats WHERE chat_id=%s', (str(chat_id),))
    result = cursor.fetchall()

    if result:
        cursor.execute("UPDATE chats SET " + name + " = %s, " + condition + " = %s WHERE chat_id=%s",
                       (str(value), str(value_condition), str(chat_id)))
    else:
        cursor.execute('INSERT INTO chats(chat_id,' + name + ',' + condition + ') VALUES(%s,%s,%s)',
                       (str(chat_id), str(value), str(value_condition)))

    conn.commit()


def save_to_db(chat_id, name, value, t):
    global set_val
    cursor = conn.cursor()
    if name == "актера":
        name = "ex_actors"
    if name == "жанр":
        name = "ex_janre"
    if name == "страну":
        name = "ex_country"
    cursor.execute('SELECT chats.' + name + ' FROM chats WHERE chat_id=%s', (str(chat_id),))
    result = cursor.fetchall()
    if result:
        if result[0][0]:
            ex_result_default = result[0][0]
            if t == "!исключить":
                ex_result = result[0][0].split(';')
                ex_result.remove('')
                for ex in ex_result:
                    if ex.lower() == value.lower()[:-1]:
                        return False
                set_val = ex_result_default + value.lower()
            elif t == "!вернуть":
                set_val = ex_result_default[0:ex_result_default.find(value)] + \
                          ex_result_default[ex_result_default.find(value) + len(value):]
        else:
            set_val = value

        cursor.execute("UPDATE chats SET " + name + " = %s WHERE chat_id=%s",
                       (str(set_val), str(chat_id)))
    else:
        cursor.execute('INSERT INTO chats(chat_id,' + name + ') VALUES(%s,%s)',
                       (str(chat_id), str(value.lower())))
    conn.commit()


def save_movies_to_db(chat_id, man_id, movies):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT users.movies FROM users WHERE chat_id=%s AND user_id=%s', (str(chat_id),
                                                                                          str(man_id)
                                                                                          ))
        result = cursor.fetchall()
        if result:
            cursor.execute("UPDATE users SET movies = %s WHERE chat_id=%s AND user_id=%s", (str(movies),
                                                                                            str(chat_id),
                                                                                            str(man_id),
                                                                                            ))
        else:
            cursor.execute('INSERT INTO users(user_id,chat_id,movies) VALUES(%s,%s,%s)', (str(man_id),
                                                                                          str(chat_id),
                                                                                          str(movies)))
        conn.commit()
        return True
    except:
        return False


def use_db(chat_id):
    cursor = conn.cursor()
    cursor.execute('SELECT '
                   'chats.ex_rating, '
                   'chats.ex_rating_condition,'
                   'chats.ex_janre,'
                   'chats.ex_year,'
                   'chats.ex_year_condition,'
                   'chats.ex_time,'
                   'chats.ex_time_condition,'
                   'chats.ex_actors,'
                   'chats.ex_country,'
                   'chats.notify'
                   ' FROM chats WHERE chat_id=%s', (str(chat_id),))
    result = cursor.fetchall()
    return result


def use_db_for_movies(user_id, chat_id):
    cursor = conn.cursor()
    if chat_id:
        cursor.execute('SELECT users.movies FROM users WHERE chat_id=%s AND user_id=%s', (str(chat_id), str(user_id)))
    else:
        cursor.execute('SELECT users.movies,users.chat_id FROM users WHERE user_id=%s', (str(user_id),))
    result = cursor.fetchall()
    return result


def notify_db(chat_id, notify):
    cursor = conn.cursor()
    cursor.execute('SELECT notify FROM chats WHERE chat_id=%s', (str(chat_id)))
    result = cursor.fetchall()
    if result:
        cursor.execute("UPDATE chats SET notify = %s WHERE chat_id=%s",
                       (str(notify), str(chat_id)))
    else:
        cursor.execute('INSERT INTO chats(chat_id,notify) VALUES(%s,%s)',
                       (str(chat_id), str(notify)))
    conn.commit()
