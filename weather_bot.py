import os
from dotenv import load_dotenv
import telebot
import requests
import json
import sqlite3
from telebot import types

load_dotenv()

bot = telebot.TeleBot(os.getenv("bot"))
api_key = os.getenv("api_key")

user_in_registration = []

conn = sqlite3.connect('wthr.sql')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS weather_us (id int auto_increment primary key, user_id varchar(50), city varchar(50))')
conn.commit()
cur.close()
conn.close()

line = ('-' * 30)

def get_main_menu():

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.InlineKeyboardButton("my city")
    btn2 = types.InlineKeyboardButton("help")
    markup.add(btn1, btn2)
    return markup

def send_weather(chat_id,city,show_menu=False):


    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&')


    if res.status_code == 200:

        res_data = json.loads(res.text)

        icon_code = res_data['weather'][0]['icon']
        icon_url = f'https://openweathermap.org/img/wn/{icon_code}@4x.png'

        caption_text = f"in city {res_data['name']} weather is {res_data['weather'][0]['description']}\n{line}\ntemperature right now : {res_data['main']['temp']} °C\n{line}\ntemperature feels like : {res_data['main']['feels_like']} °C\n{line}\nwind speed : {res_data['wind']['speed']} m/s\n{line}\nhumidity : {res_data['main']['humidity']} %\n{line}\nto know weather in another city just type name of city in chat"

        markup = get_main_menu() if show_menu else None

        bot.send_photo(chat_id,icon_url,caption = caption_text,reply_markup=markup)

    else:

        markup = get_main_menu() if show_menu else None

        bot.send_message(chat_id,"no city named like that",reply_markup=markup)

@bot.message_handler(commands=['help'])

def help_command(message):

    help_text = f"how to use bot:\n{line}\n/start - start bot\n{line}\n/reset - reset your data\n{line}\n/help - info about bot\n{line}\ntype the name of city to find out the weather"

    bot.send_message(message.chat.id, help_text, parse_mode='Markdown', reply_markup=get_main_menu())

@bot.message_handler(commands=['reset'])

def reset(message):

    conn = sqlite3.connect('wthr.sql')
    cur = conn.cursor()

    cur.execute('DELETE FROM weather_us WHERE user_id = ?', (str(message.from_user.id),))
    conn.commit()

    cur.close()

    conn.close()


    markup = types.ReplyKeyboardRemove()

    bot.send_message(message.chat.id,"data reset",reply_markup=markup)

@bot.message_handler(commands=['start'])

def start(message):

    user_in_registration.append(message.from_user.id)

    conn = sqlite3.connect('wthr.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS weather_us (id int auto_increment primary key, user_id varchar(50), city varchar(50))')
    conn.commit()
    cur.execute('SELECT city FROM weather_us WHERE user_id = ?',(message.from_user.id,))

    user_data = cur.fetchone()


    if user_data:

        saved_city = user_data[0]
        bot.send_message(message.chat.id, f"you are registered ! your home - city : {saved_city.capitalize()}. \n")

        send_weather(message.chat.id, saved_city, show_menu=True)

        if message.from_user.id in user_in_registration:
            user_in_registration.remove(message.from_user.id)

        cur.close()
        conn.close()

    else:

        cur.close()
        conn.close()

        bot.send_message(message.chat.id,f"hi , {message.from_user.username} , to use this bot , enter your home-city :")
        bot.register_next_step_handler(message, get_city)

def get_city(message):

    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&')

    if res.status_code == 200:

        conn = sqlite3.connect('wthr.sql')
        cur = conn.cursor()

        cur.execute(f'INSERT INTO weather_us (user_id, city) VALUES (?, ?)', (message.from_user.id, city))

        conn.commit()
        cur.close()
        conn.close()

        user_in_registration.remove(message.from_user.id)
        bot.send_message(message.chat.id,"you have been registered")

        send_weather(message.chat.id, city, show_menu=True)

    else:

        bot.reply_to(message, "wrong city ! try again")
        bot.register_next_step_handler(message, get_city)

@bot.message_handler(content_types='text')

def get_weather(message):

    if message.from_user.id in user_in_registration:
        return

    conn = sqlite3.connect('wthr.sql')
    cur = conn.cursor()
    cur.execute('SELECT city FROM weather_us WHERE user_id = ?', (str(message.from_user.id),))
    user_data = cur.fetchone()
    cur.close()
    conn.close()

    if not user_data:

        bot.send_message(message.chat.id, "register firstly ! type /start")
        return

    if message.text == "help":

        help_command(message)
        return

    if message.text == "my city":
        send_weather(message.chat.id, user_data[0], show_menu=True)
        return

    send_weather(message.chat.id, message.text.strip().lower(), show_menu=True)

bot.infinity_polling()
