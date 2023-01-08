import asyncio
import logging
import gspread
from pyrogram import Client, filters, types
from questions import questions, answer_variant
logging.basicConfig(level=logging.INFO)
api_id = 9411854
api_hash = '499c76606cefdeadd4b1ece84a5a9932'
API_TOKEN = '1817474310:AAFd3zZ0KF6_GdsBqgy-I1QtdyvCDGO7d5Y'
app = Client('bot', bot_token= API_TOKEN, api_id= api_id, api_hash= api_hash)
gc = gspread.service_account('credentials.json')
email = 'proektnya.pochta@gmail.com'
table_url = 'https://docs.google.com/spreadsheets/d/1PWRXWUcxjPZHiw6BBm4dJrUR_Mk5gCIp2bJDPXN5IQI/edit#gid=376448824'
sh = gc.open_by_url(table_url)
def get_answer_kb(chat_id):
    answer_kb = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text=answer_variant[0], callback_data=f'answer-0-{chat_id}')],
    [types.InlineKeyboardButton(text=answer_variant[1], callback_data=f'answer-1-{chat_id}')],
    [types.InlineKeyboardButton(text=answer_variant[2], callback_data=f'answer-2-{chat_id}')],
    [types.InlineKeyboardButton(text=answer_variant[3], callback_data=f'answer-3-{chat_id}')],
    [types.InlineKeyboardButton(text=answer_variant[4], callback_data=f'answer-4-{chat_id}')],
    ])
    return answer_kb
def check_existing_sheet(sheet_name):
    sh = gc.open_by_url(table_url)
    worksheet_list = sh.worksheets()
    for i in range(len(worksheet_list)):
        worksheet_list[i]= worksheet_list[i].title
    return sheet_name in worksheet_list
def create_sheet_poll(sheet_name, deadline, author_id, members, chat_name):
    sh = gc.open_by_url(table_url)
    worksheet = sh.add_worksheet(title=str(sheet_name), rows=100, cols=20)
    worksheet.append_row(['id создателя опроса', 'Дедлайн(в часах)', 'Название чата', 'Активный опрос'])
    worksheet.append_row([author_id,deadline, chat_name, 1])
    worksheet.append_row(['username участника группы','id участника группы'] + [str(i) for i in range(1,11)] + ['У','Удовлетворённость'])
    for row in range(len(members)):
        worksheet.append_row(members[row] + ['' for i in range(1,11)])
def change_poll_status(chat_id,status):
    sh = gc.open_by_url(table_url)
    worksheet = sh.worksheet(str(chat_id))
    worksheet.update_cell(row=2,col=4, value=status)
async def write_answer(chat_id,user_id, question_num,answer):
    sh = gc.open_by_url(table_url)
    worksheet = sh.worksheet(str(chat_id))
    cell = worksheet.find(user_id)
    worksheet.update_cell(row = cell.row, col=question_num+2, value=answer)
def get_user_current_question(chat_id,user_id):
    sh = gc.open_by_url(table_url)
    worksheet = sh.worksheet(str(chat_id))
    cell = worksheet.find(user_id)
    row_number = cell.row
    values_list = worksheet.row_values(row_number)
    next_question = None
    for i in range(1 , 11):
        if not (values_list[ i + 2 ]):
            next_question = i
            break
    return next_question
def get_users_for_notification():
    users = list()
    sh = gc.open_by_url(table_url)
    worksheets = sh.worksheets()
    for sheet in worksheets:
        if sheet.title == 'example':
            continue
        chat_id = sheet.title
        sheet = sh.worksheet(chat_id)
        if sheet.cell(row = 2, col=4).value == 1:
            continue
        for user_id in sheet.col_values(2)[3:]:
            if get_user_current_question(chat_id,int(user_id)):
                users.append([chat_id,user_id])
    return users
async def notificate_users():
    users = get_users_for_notification()
    for user in users:
        await send_poll_notification(user[0], user[1])
async def send_poll_notification(chat_id, user_id):

    chat = await app.get_chat(chat_id)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text='Перейти к прохождению опроса', callback_data=f'get_question-{str(chat_id)}')]])

    await app.send_message(chat_id=user_id, text=f'В группе {chat.title} проводится опрос', reply_markup=kb)

@app.on_callback_query()
async def get_query(client: Client, callback_query: types.CallbackQuery):
    if callback_query.data.startswith('get_question-'):
        chat_id = int(callback_query.data.split('-')[-1])
        user_id = callback_query.message.chat.id
        question = get_user_current_question(chat_id,user_id)
        await app.delete_messages(chat_id=user_id, message_ids=callback_query.message.id)
        if question > 10:
            await app.send_message(chat_id=user_id, text='Вы прошли опрос, спасибо.')
            return True
        answer_kb =get_answer_kb(chat_id)
        await app.send_message(chat_id=user_id,text=questions[question-1], reply_markup=answer_kb)
    elif callback_query.data.startswith('answer-'):
        chat_id = int(callback_query.data.split('-')[-1])
        user_id = callback_query.message.chat.id
        answer_variant =int(callback_query.data.split('-')[1])
        question_num = get_user_current_question(chat_id=chat_id, user_id=user_id)
        await write_answer(chat_id=chat_id,user_id=user_id, question_num=question_num,answer=answer_variant)
        await app.delete_messages(chat_id=user_id , message_ids=callback_query.message.id)
        if question_num >= 10:
            await app.send_message(chat_id=user_id , text='Вы прошли опрос, спасибо.')
            return True
        question_num = get_user_current_question(chat_id=chat_id, user_id= callback_query.message.chat.id)
        answer_kb = get_answer_kb(chat_id)
        await app.send_message(chat_id=user_id, text = questions[question_num-1], reply_markup=answer_kb)



@app.on_message(filters=filters.group & filters.command('setup'))
async def setup(client : Client, message: types.Message):
    print(message.chat.id)
    if check_existing_sheet(sheet_name=str(message.chat.id)):
        await message.reply('Для данной группы уже установлено проведение опросов')
    else:
        if len(message.text.split()) == 2:
            deadline = message.text.split()[-1]
            if deadline.isdigit():
                await message.reply(f'Успешно было запущено проведение опросов в этой группе. Время проведения опросов(в часах): {message.text.split()[-1]}')
                chat_members = list()
                async for member in app.get_chat_members(message.chat.id):
                    chat_members.append([member.user.username, member.user.id])
                create_sheet_poll(sheet_name=message.chat.id, deadline = deadline, author_id= message.from_user.id, members= chat_members, chat_name= message.chat.title)
            else:
                await message.reply('Введённый параметр не является числом.')
        else:
            await message.reply('Неверный формат команды. Команда должна выглядеть так: \"/setup время_проведения_опроса(в часах)\"')
app.run()