import requests
from data.user import User
from data import db_session
import datetime
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

token = '6050553629:AAGFy-_9u2F5oVjHO0IQtUAejdPbylxfNPY'
bot = Bot(token)
dp = Dispatcher(bot)

VALUTES = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()

buttons_currencies = []

logger = logging.getLogger(__name__)


# start функция
@dp.message_handler(commands=['start'])
async def command_start_handler(message: Message):
    await message.answer(f'Привет, {message.from_user.full_name}!')
    list_id = [i.id for i in DB_SESS.query(User).all()]
    if message.chat.id not in list_id:
        user = add_new_user(message)
    if not DB_SESS.query(User).filter(User.id == message.chat.id).first().valutes:
        await message.answer('Введите через пробел, какие валюты вас интересуют(пример: USD RUB)')
    else:
        await message.answer('Введите валюту курс которой вы хотите узнать')


# функция добавления списка валют


@dp.message_handler(lambda message: all(i in VALUTES['Valute'] for i in message.text.split())
                                    and len(message.text.split()) > 1
                                    and DB_SESS.query(User).filter(User.id == message.chat.id).first().valutes == '')
async def add_list_valutes(message: types.Message):
    await message.answer('Список валют принят')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons_currencies = message.text.split()
    keyboard.add(*buttons_currencies)
    add_list_valutes_user(message)
    await message.answer('Нажмите на валюту и узнайте ее курс', reply_markup=keyboard)


# функция help

@dp.message_handler(commands=['help'])
async def command_start_handler(message: Message):
    await message.answer('/new_list_valutes - создать новый список валют')
    await message.answer('/replace - замена одной валюты в списке на другую')


# функция замены списка валют


@dp.message_handler(commands=['new_list_valutes'])
async def replace_list_valutes(message: Message):
    if DB_SESS.query(User).filter(User.id == message.chat.id).first().is_developer:
        new_list_valutes = message.text.split()[1::]
        if all(i in VALUTES['Valute'] for i in new_list_valutes):
            edit_list_valutes_user(message, ' '.join(new_list_valutes))
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*new_list_valutes)
            await message.answer('Список валют отредактирован', reply_markup=keyboard)
        else:
            await message.answer('Какая-то из валют введена неверно')
    else:
        await message.answer('Вы не можете редактировать список валют')


# функция замены одной валюты из списка валют


@dp.message_handler(commands=['replace'])
async def edit_list_valutes(message: Message):
    if DB_SESS.query(User).filter(User.id == message.chat.id).first().is_developer:
        current_user = DB_SESS.query(User).filter(User.id == message.chat.id).first()
        valutes = message.text.split()
        list_valutes = current_user.valutes.split()
        if len(valutes) == 3:
            if valutes[2] in VALUTES['Valute'] and valutes[1] in list_valutes:
                list_valutes[list_valutes.index(valutes[1])] = valutes[2]
                current_user.valutes = ' '.join(list_valutes)
                DB_SESS.merge(current_user)
                DB_SESS.commit()
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(*current_user.valutes.split())
                await message.answer('Список валют отредактирован', reply_markup=keyboard)
            else:
                await message.answer('Какая-то из валют введена неверно')
    else:
        await message.answer('Вы не можете редактировать список валют')


# функция отображения курса валюты


@dp.message_handler(lambda message: message.text in
                                    DB_SESS.query(User).filter(User.id == message.chat.id).first().valutes)
async def see_currencies(message: types.Message):
    await message.reply(VALUTES['Valute'][message.text]['Value'])


# функция добавления нового пользователя в базу данных


def add_new_user(message):
    user = User(
        id=message.chat.id,
        name=message.from_user.full_name
    )
    DB_SESS.add(user)
    DB_SESS.commit()
    return user


# функция добавления списка валют в базу данных


def add_list_valutes_user(message):
    current_user = DB_SESS.query(User).filter(User.id == message.chat.id).first()
    current_user.valutes = message.text
    DB_SESS.merge(current_user)
    DB_SESS.commit()
    return current_user


# функция редактирования списка валют


def edit_list_valutes_user(message, new_list_valutes):
    current_user = DB_SESS.query(User).filter(User.id == message.chat.id).first()
    current_user.valutes = new_list_valutes
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
