import sqlite3
def get_conn():
    conn = sqlite3.connect('mydatabase.db')
    return conn

def create_main_table():
    query = '''CREATE TABLE IF NOT EXISTS poll_groups(
    chat_id INT PRIMARY KEY,
    chat_title  TEXT,
    creator_id INT,
    deadline INT,
    active_poll INT);'''
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
    Y INT DEFAULT 0);'''
    conn = get_conn()
    conn.cursor().execute(query)
    conn.commit()
    for member in members:
        query = f'''INSERT INTO '{chat_id}' (member_id, member_username)
    VALUES({member[0]},'{member[1]}');'''
        conn.cursor().execute(query)
        conn.commit()
def add_chat(chat_id: int, chat_title : str, creator_id : int, deadline: int):
    query = f'''INSERT INTO poll_groups VALUES({chat_id}, '{chat_title}', {creator_id}, {deadline}, 1);'''
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
        query = f'''SELECT member_id FROM '{chat_id}' WHERE questions_answered < 10;'''
        for user in conn.cursor().execute(query).fetchall():
            users.append([chat_id,user[0]])
    return users
def new_poll(chat_id:int, members:list):
    query = f'''DELETE FROM '{chat_id}';'''
    conn = get_conn()
    conn.cursor().execute(query)
    conn.commit()
    change_status(chat_id=chat_id, status=1)
    for member in members:
        query = f'''INSERT INTO '{chat_id}' (member_id, member_username)
    VALUES({member[0]},'{member[1]}');'''
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
def get_response(chat_id: int):
    query = f'''SELECT * FROM '{chat_id}';'''
    conn = get_conn()
    data = conn.cursor().execute(query).fetchall()
    for i in range(len(data)):
        Y = sum(data[i][3:13])/data[i][2]
        data[i] = list(data[i]) + [Y]
        if Y >= 3:
            data[i].append('Высокая удовлетворённость')
        elif Y >= 2:
            data[i].append('Средняя удовлетворённость')
        else:
            data[i].append('Низкая удовлетворённсть')
    return data