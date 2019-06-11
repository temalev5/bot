#import sqlite3
import psycopg2
import os

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

def saveToBDset(chat_id,name,condition,value):
    cursor = conn.cursor()
    value_condition=condition
    if (name=="рейтинг"):
        name = "ex_rating"
        condition = "ex_rating_condition"
    if (name =="время"):
        name = "ex_time"
        condition = "ex_time_condition"
    if (name =="год"):
        name = "ex_year"
        condition = "ex_year_condition"

    cursor.execute('SELECT chats.' + name + ' FROM chats WHERE chat_id=?', (chat_id,))
    result = cursor.fetchall()

    if (result):
        cursor.execute("UPDATE chats SET " + name + " = ?, "+ condition +" = ? WHERE chat_id=?",
                       (value, value_condition, chat_id))
    else:
        cursor.execute('INSERT INTO chats(chat_id,' + name + ','+condition+') VALUES(?,?,?)',
                       (chat_id, value,value_condition))

    conn.commit()


def saveToBD(chat_id,name,value,t):
    cursor = conn.cursor()
    if (name == "актера"): name = "ex_actors"
    if (name == "жанр"): name = "ex_janre"
    if (name == "страну"): name = "ex_country"
    cursor.execute('SELECT chats.'+ name +' FROM chats WHERE chat_id=?', (chat_id,))
    result = cursor.fetchall()
    if (result):
        if (result[0][0]):
            ex_result_default = result[0][0]
            if (t=="!исключить"):
                ex_result = result[0][0].split(';')
                ex_result.remove('')
                for ex in ex_result:
                    if (ex.lower() == value.lower()[:-1]):
                        return False
                setvalue = ex_result_default+value.lower()
            elif (t=="!вернуть"):
                setvalue = ex_result_default[0:ex_result_default.find(value)]+ex_result_default[ex_result_default.find(value)+len(value):]
        else:
            setvalue = value

        cursor.execute("UPDATE chats SET "+name+" = ? WHERE chat_id=?",
                       (setvalue,chat_id))
    else:
        cursor.execute('INSERT INTO chats(chat_id,'+name+') VALUES(?,?)',
                       (chat_id,value.lower()))
    conn.commit()

def saveBD(chat):
    cursor = conn.cursor()
    for i in range(len(chat.man)):
        movies = ""
        cursor.execute('SELECT users.movies FROM users WHERE chat_id=? AND user_id=?', (chat.chat_id,chat.man[i].man_id))
        result = cursor.fetchall()
        for j in range(len(chat.man[i].movies)):
            movies += chat.man[i].movies[j].title + "(" + str(chat.man[i].movies[j].id) + ")" + ";"
        if (movies==""):
            break
        if (result):
            cursor.execute("UPDATE users SET movies = ? WHERE chat_id=? AND user_id=?", (movies,chat.chat_id,chat.man[i].man_id,))
        else:
            cursor.execute('INSERT INTO users(user_id,chat_id,movies) VALUES(?,?,?)', (chat.man[i].man_id,chat.chat_id,movies))
        conn.commit()


def useDB(chat_id):
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
                   'chats.ex_country'
                   ' FROM chats WHERE chat_id=?', (chat_id,))
    result = cursor.fetchall()
    return result

def useDBForMovies(user_id,chat_id):
    cursor = conn.cursor()
    cursor.execute('SELECT users.movies FROM users WHERE chat_id=? AND user_id=?', (chat_id,user_id) )
    result = cursor.fetchall()
    return result