import sqlite3
import time
import datetime
def get_conn():
    conn = sqlite3.connect('mydatabase.db')
    return conn

def create_main_table():
    query = '''CREATE TABLE IF NOT EXISTS poll_groups(
    chat_id INT PRIMARY KEY,
    chat_title  TEXT,
    creator_id INT,
    deadline INT,
    active_poll INT,
    expire_time INT);'''
    conn = get_conn()
    conn.cursor().execute(query)
    conn.commit()
def create_history_table(chat_id : int):
    query = f'''CREATE TABLE IF NOT EXISTS 'history_{chat_id}'(
    month INT,
    Y_low INT,
    Y_medium INT,
    Y_high INT
);'''
    conn = get_conn()
    conn.cursor().execute(query)
    conn.commit()
def create_poll_table(chat_id : int, members:list):
    query = f'''CREATE TABLE IF NOT EXISTS '{chat_id}'(
    member_id INT PRIMARY KEY,
    member_username INT,
    questions_answered INT DEFAULT 0,
    question_1 INT DEFAULT 0,
    question_2 INT DEFAULT 0,
    question_3 INT DEFAULT 0,
    question_4 INT DEFAULT 0,
    question_5 INT DEFAULT 0,
    question_6 INT DEFAULT 0,
    question_7 INT DEFAULT 0,
    question_8 INT DEFAULT 0,
    question_9 INT DEFAULT 0,
    question_10 INT DEFAULT 0,
    last_activity INT);'''
    conn = get_conn()
    conn.cursor().execute(query)
    conn.commit()
    for member in members:
        query = f'''INSERT INTO '{chat_id}' (member_id, member_username)
    VALUES({member[0]},'{member[1]}');'''
        conn.cursor().execute(query)
        conn.commit()
    create_history_table(chat_id=chat_id)
def add_chat(chat_id: int, chat_title : str, creator_id : int, deadline: int):
    query = f'''INSERT INTO poll_groups VALUES({chat_id}, '{chat_title}', {creator_id}, {deadline}, 1, {int(time.time())+deadline*60});'''
    conn = get_conn()
    conn.cursor().execute(query)
    conn.commit()
def get_status(chat_id:int):
    query = f'''SELECT active_poll FROM poll_groups WHERE chat_id = {chat_id};'''
    conn = get_conn()
    return conn.cursor().execute(query).fetchone()[0]
def check_existing_sheet(chat_id:int):
    query = f'''SELECT chat_id FROM poll_groups WHERE chat_id={chat_id};'''
    conn = get_conn()
    if conn.cursor().execute(query).fetchall() != []:
        return True
    else:
        return False
def get_author_id(chat_id: int):
    query = f'''SELECT creator_id FROM poll_groups WHERE chat_id = {chat_id}'''
    conn = get_conn()
    data = conn.cursor().execute(query).fetchall()
    return data[0][0]
def check_full_done(chat_id:int):
    query = f'''SELECT questions_answered FROM '{chat_id}';'''
    conn = get_conn()
    answers = conn.cursor().execute(query).fetchall()
    for answer in answers:
        if answer[0] != 10:
            return False
    return True

def change_status(chat_id: int, status : int):
    query = f'''UPDATE poll_groups SET active_poll = {status} WHERE chat_id = {chat_id};'''
    conn = get_conn()
    conn.cursor().execute(query)
    conn.commit()

def write_answer(chat_id : int, user_id : int, question_number : int, answer : int):
    query = f'''UPDATE '{chat_id}' SET question_{question_number} = {answer} WHERE member_id = {user_id};'''
    conn = get_conn()
    conn.cursor().execute(query)
    query = f'''UPDATE '{chat_id}' SET questions_answered = {question_number} WHERE member_id = {user_id};'''
    conn.cursor().execute(query)
    query = f'''UPDATE '{chat_id}' SET last_activity = {int(time.time())} WHERE member_id = {user_id};'''
    conn.cursor().execute(query)
    conn.commit()
def get_user_current_question(chat_id : int, user_id : int):
    query = f'''SELECT questions_answered FROM '{chat_id}' WHERE member_id = {user_id};'''
    conn = get_conn()
    return conn.cursor().execute(query).fetchone()[0]
def get_users_for_notification():
    users = list()
    query = f'''SELECT chat_id FROM poll_groups WHERE active_poll = 1;'''
    conn = get_conn()
    chat_ids = conn.cursor().execute(query).fetchall()
    for chat in chat_ids:
        chat_id = chat[0]
        query = f'''SELECT member_id, last_activity FROM '{chat_id}' WHERE questions_answered < 10;'''
        for user in conn.cursor().execute(query).fetchall():
            if int(time.time()) - user[1] > 10 * 60:
                users.append([chat_id,user[0]])
    return users
def new_poll(chat_id:int, members:list):
    query = f'''DELETE FROM '{chat_id}';'''
    conn = get_conn()
    conn.cursor().execute(query)
    conn.commit()
    change_status(chat_id=chat_id, status=1)
    for member in members:
        query = f'''INSERT INTO '{chat_id}' (member_id, member_username, last_activity)
    VALUES({member[0]},'{member[1]}',{time.time()});'''
        conn.cursor().execute(query)
        conn.commit()
def get_inactive_polls():
    query = f'''SELECT chat_id FROM poll_groups WHERE active_poll = 0;'''
    conn = get_conn()
    return conn.cursor().execute(query).fetchall()
def get_active_polls():
    query = f'''SELECT chat_id FROM poll_groups WHERE active_poll = 1;'''
    conn = get_conn()
    return conn.cursor().execute(query).fetchall()
def check_expired_poll(chat_id : int):
    query = f'''SELECT expire_time FROM poll_groups WHERE chat_id = {chat_id};'''
    conn = get_conn()
    data = conn.cursor().execute(query).fetchall()[0][0]
    if data < time.time():
        return True
    return False
def get_history_response(chat_id: int):
    conn = get_conn()
    query = f'''SELECT * FROM "history_{chat_id}"'''
    data = conn.cursor().execute(query).fetchall()
    if len(data) >= 2:
        if len(data) > 5:
            data = data[-1:-6:-1].reverse()
        else:
            data = data[-1::-1].reverse()

    return data

def get_response(chat_id: int):
    query = f'''SELECT * FROM '{chat_id}';'''
    conn = get_conn()
    data = conn.cursor().execute(query).fetchall()
    summa = 0
    total = len(data)
    if total == 0:
        total = 1
    counter = [0,0,0]
    for i in range(len(data)):
        if data[i][2] == 0:
            Y = 0
        else:
            Y = sum(data[i][3:13])/data[i][2]
            summa += Y
        data[i] = list(data[i]) + [Y]
        if Y >= 3:
            data[i].append('Высокая удовлетворённость')
            counter[2] += 1
        elif Y >= 2:
            data[i].append('Средняя удовлетворённость')
            counter[1] += 1
        else:
            data[i].append('Низкая удовлетворённсть')
            counter[0] += 1
    query = f'''INSERT INTO 'history_{str(chat_id)}' VALUES({datetime.datetime.now().month}, {counter[0]}, {counter[1]}, {counter[2]});'''
    conn = get_conn()

    conn.cursor().execute(query)
    conn.commit()

    data = [['id пользователя', 'username пользователя', 'На вопросов отвечено', 'Вопрос 1', 'Вопрос 2',
             'Вопрос 3', 'Вопрос 4', 'Вопрос 5', 'Вопрос 6', 'Вопрос 7', 'Вопрос 8', 'Вопрос 9',
             'Вопрос 10', 'У', 'Уровень удовлетворённости']] + data + [['Итого' ,'' ,'' ,'' ,'' ,'','','','','','','','',str(summa/total)]]
    return data