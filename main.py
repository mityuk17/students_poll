import datetime
import logging

import pyrogram.errors.exceptions.bad_request_400

import db
import draw_pie
import openpyxl
import os
from draw_pie import draw
import gspread
from pyrogram import Client, filters, types
from questions import questions, answer_variant
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
logging.basicConfig(level=logging.INFO)
api_id = 0
api_hash = ''
API_TOKEN = ''
app = Client('bot', bot_token= API_TOKEN, api_id= api_id, api_hash= api_hash)

job_defaults = {
    'coalesce': False,
    'max_instances': 30
}
scheduler = AsyncIOScheduler(job_defaults=job_defaults)
def get_answer_kb(chat_id):
    answer_kb = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text=answer_variant[0], callback_data=f'answer=0={chat_id}')],
    [types.InlineKeyboardButton(text=answer_variant[1], callback_data=f'answer=1={chat_id}')],
    [types.InlineKeyboardButton(text=answer_variant[2], callback_data=f'answer=2={chat_id}')],
    [types.InlineKeyboardButton(text=answer_variant[3], callback_data=f'answer=3={chat_id}')],
    [types.InlineKeyboardButton(text=answer_variant[4], callback_data=f'answer=4={chat_id}')],
    ])
    return answer_kb
async def sheet_expired(chat_id):
    if db.get_status(chat_id=chat_id) == 0:
        return True
    await make_conclusion(chat_id)
async def poll_expired():
    polls = db.get_active_polls()
    for poll in polls:
        if db.check_expired_poll(poll[0]):
            await make_conclusion(poll[0])
async def poll_finished():
    polls = db.get_active_polls()
    for poll in polls:
        if db.check_full_done(poll[0]):
            await make_conclusion(poll[0])

async def make_conclusion(chat_id):
    response = db.get_response(chat_id=chat_id)
    db.change_status(chat_id=chat_id,status=0)
    draw_pie.draw(data = response, chat_id=chat_id)
    if not os.path.exists('responses'):
        os.mkdir('responses')
    if os.path.exists(f'responses/{chat_id}.xlsx'):
        os.remove(f'responses/{chat_id}.xlsx')
    wb = openpyxl.Workbook()
    ws = wb.active
    for row in response:
        ws.append(row)
    wb.save(f'responses/{chat_id}.xlsx')
    author_id = db.get_author_id(chat_id=chat_id)
    draw_pie.draw2(data=db.get_history_response(chat_id=chat_id),chat_id=chat_id)
    chat = await app.get_chat(chat_id=chat_id)
    print(response)
    await app.send_message(chat_id=author_id,text=f'''Опрос в группе {chat.title} проведён
Людей опрошено: {len(response)-1}
Людей ответило на все вопросы: {len([i for i in response if i[2]==10])}''')
    await app.send_photo(chat_id=author_id, photo=f'plots/pie_{chat_id}.png')
    await app.send_photo(chat_id=author_id, photo=f'plots/bar_{chat_id}.png')
    await app.send_document(chat_id=author_id,document=f'responses/{chat_id}.xlsx', caption='Отчёт по опросу в формате .xlsx')
    os.remove(f'plots/{chat_id}.png')
async def start_polls():
    polls = db.get_inactive_polls()
    for poll in polls:
        chat_members = list()
        async for member in app.get_chat_members(poll[0]):
            if not member.user.is_bot:
                chat_members.append([ member.user.id , member.user.username ])
        db.new_poll(chat_id = poll[0], members=chat_members)
async def notificate_users():
    users = db.get_users_for_notification()
    print(users)
    for user in users:
        chat = await app.get_chat(chat_id=user[0])
        await send_poll_notification(user[0], user[1])
async def send_poll_notification(chat_id, user_id):
    chat = await app.get_chat(chat_id)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text='Перейти к прохождению опроса', callback_data=f'get_question={str(chat_id)}')]])
    try:
        await app.send_message(chat_id=user_id, text=f'В группе {chat.title} проводится опрос', reply_markup=kb)
        print(True, user_id)
    except pyrogram.errors.exceptions.bad_request_400.PeerIdInvalid:
        print(1)
        return False
    except pyrogram.errors.exceptions.bad_request_400.InputUserDeactivated:
        print(2)
        return False

@app.on_callback_query()
async def get_query(client: Client, callback_query: types.CallbackQuery):
    if callback_query.data.startswith('get_question='):
        chat_id = int(callback_query.data.split('=')[-1])
        user_id = callback_query.message.chat.id
        question = db.get_user_current_question(chat_id,user_id)
        #await app.delete_messages(chat_id=user_id, message_ids=callback_query.message.id)
        if question >= 10:
            await app.send_message(chat_id=user_id, text='Вы прошли опрос, спасибо.')
            return True
        answer_kb =get_answer_kb(chat_id)
        await app.send_message(chat_id=user_id,text=questions[question], reply_markup=answer_kb)
    elif callback_query.data.startswith('answer='):
        chat_id = int(callback_query.data.split('=')[-1])
        user_id = callback_query.message.chat.id
        answer_variant =int(callback_query.data.split('=')[1])
        question_num = db.get_user_current_question(chat_id=chat_id, user_id=user_id)
        db.write_answer(chat_id=chat_id,user_id= user_id,question_number=question_num+1, answer=answer_variant)
        if question_num >= 9:
            await app.send_message(chat_id=user_id , text='Вы прошли опрос, спасибо.')
            return True
        question_num = db.get_user_current_question(chat_id=chat_id, user_id= callback_query.message.chat.id)
        answer_kb = get_answer_kb(chat_id)
        await app.send_message(chat_id=user_id, text = questions[question_num], reply_markup=answer_kb)



@app.on_message(filters=filters.group & filters.command('setup'))
async def setup(client : Client, message: types.Message):
    print(message.chat.id)
    if db.check_existing_sheet(chat_id= message.chat.id):
        await message.reply('Для данной группы уже установлено проведение опросов')
    else:
        if len(message.text.split()) == 2:
            deadline = message.text.split()[-1]
            if deadline.isdigit():
                chat_members = list()
                async for member in app.get_chat_members(message.chat.id):
                    if not member.user.is_bot:
                        if member.user.id != message.from_user.id:
                            chat_members.append([member.user.id, member.user.username])
                db.add_chat(chat_id=message.chat.id,chat_title=message.chat.title,creator_id=message.from_user.id, deadline=int(deadline))
                db.create_poll_table(chat_id=message.chat.id, members=chat_members)
                await message.reply(f'Успешно было запущено проведение опросов в этой группе. Время проведения опросов(в часах): {message.text.split()[-1]}\nЧтобы бот мог отправить вам сообщение с опросом перейдите по ссылке и нажмите кнопку Начать\nhttps://t.me/ContentedStudentBot?start')
            else:
                await message.reply('Введённый параметр не является числом.')
        else:
            await message.reply('Неверный формат команды. Команда должна выглядеть так: \"/setup время_проведения_опроса(в часах)\"')
db.create_main_table()
scheduler.add_job(poll_expired, 'interval', minutes = 5)
scheduler.add_job(poll_finished, 'interval',minutes =1)
scheduler.add_job(start_polls, 'cron', minute = 30)
scheduler.add_job(notificate_users, 'interval', minutes = 3)
scheduler.start()
app.run()
