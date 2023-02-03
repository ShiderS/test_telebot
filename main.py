import telebot
import requests

token = '6050553629:AAGFy-_9u2F5oVjHO0IQtUAejdPbylxfNPY'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'], content_types=['text'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет')
    bot.send_message(message.chat.id, 'Я телеграмм бот')
    bot.send_message(message.chat.id, 'Я был создан для проверки работоспособности библиотеки telebot')
    bot.send_message(message.chat.id, 'Пожлуйста, напишите мне свое имя:')


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, f"Привет {message.text}!")


bot.polling(none_stop=True)
