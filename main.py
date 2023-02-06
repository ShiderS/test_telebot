import aiogram
import requests
from data.user import User
from data import db_session
import datetime
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

# создаем бота в BotFather и копируем токен
token = '6050553629:AAGFy-_9u2F5oVjHO0IQtUAejdPbylxfNPY'
bot = Bot(token)
dp = Dispatcher(bot)

# подключаемся к API
VALUTES = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()

buttons_currencies = []

logger = logging.getLogger(__name__)


@dp.message_handler(commands=['start'])
async def command_start_handler(message: Message):
    await message.answer(f'Привет, {message.from_user.full_name}!')
    list_id = [i.id for i in DB_SESS.query(User).all()]
    if message.chat.id not in list_id:
        user = add_new_user(message)
    if not DB_SESS.query(User).filter(User.id == message.chat.id).first().vallutes:
        await message.answer('Введите через пробел, какие валюты вас интересуют(пример: USD RUB)')
    else:
        await message.answer('Введите валюту курс которой вы хотите узнать')


@dp.message_handler(lambda message: all(i in VALUTES['Valute'] for i in message.text.split())
                                    and len(message.text.split()) > 1
                    and DB_SESS.query(User).filter(User.id == message.chat.id).first().vallutes == '')
async def add_list_valutes(message: types.Message):
    await message.answer('Список валют принят')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons_currencies = message.text.split()
    keyboard.add(*buttons_currencies)
    add_list_vallutes_user(message)
    await message.answer('Нажмите на валюту и узнайте ее курс', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text in
                                    DB_SESS.query(User).filter(User.id == message.chat.id).first().vallutes)
async def see_currencies(message: types.Message):
    await message.reply(VALUTES['Valute'][message.text]['Value'])


def add_new_user(message):
    user = User(
        id=message.chat.id,
        name=message.from_user.full_name
    )
    DB_SESS.add(user)
    DB_SESS.commit()
    return user


def add_list_vallutes_user(message):
    current_user = DB_SESS.query(User).filter(User.id == message.chat.id).first()
    print(current_user)
    current_user.vallutes = message.text
    DB_SESS.merge(current_user)
    DB_SESS.commit()
    return current_user


@dp.message_handler(text=[''])
async def echo_handler(message: types.Message):
    try:
        # Send copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer('Nice try!')


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    db_session.global_init("db/db.db")
    DB_SESS = db_session.create_session()
    asyncio.run(main())
