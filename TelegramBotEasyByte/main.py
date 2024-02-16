import datetime
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from telebot import types
from base import bot
import time

cash = 0
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, 'Здравствуй!\nВведите сумму для перевода в другую валюту')
    bot.register_next_step_handler(message, button)


@bot.message_handler(func=lambda message: True)
def button(message):
    global cash

    try:
        cash = float(message.text.strip())
    except ValueError:
        logging.error(f'ValueError: Invalid input for cash = {cash}')
        return
    if cash > 0:
        logging.info('Cash amount is greater than 0')
        markup = types.InlineKeyboardMarkup(row_width=2)
        button1 = types.InlineKeyboardButton("USD/EUR 🎓", callback_data="usd/eur")
        button2 = types.InlineKeyboardButton("EUR/USD 🎓", callback_data="eur/usd")
        button3 = types.InlineKeyboardButton("USD/GBR 🎓", callback_data="usd/gbp")
        button4 = types.InlineKeyboardButton("Другое 🎓", callback_data="else")
        button5 = types.InlineKeyboardButton("Показать популярные валюты относительно доллара ⚖", callback_data="info")
        markup.add(button1, button2, button3, button4, button5)

        bot.send_message(message.chat.id, "Выберите курс валют", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Введите число > 0")
        bot.register_next_step_handler(message, button)


@bot.callback_query_handler(func=lambda call: True)
def callback_message(call):
    if (call.data == 'usd/eur') or (call.data == 'eur/usd') or (call.data == 'usd/gbp'):
        val = call.data.upper().split('/')
        url = f'http://api.currencylayer.com/convert?access_key=b1b1ec62288ce24ef2c336d60c4f9cef&from={val[0]}&to={val[1]}&amount={cash}'
        response = requests.get(url)
        data = response.json()
        rate = data['result']
        bot.send_message(call.message.chat.id, f'Перевел {cash} {val[0]} в {round(rate, 2)} {val[1]}')
        bot.register_next_step_handler(call.message, button)
    elif call.data == 'info':
        try:
            API_KEY = 'b1b1ec62288ce24ef2c336d60c4f9cef'
            base_url = 'http://api.currencylayer.com/live'
            current_date = datetime.datetime.now()
            formatted_date = current_date.strftime('%Y-%m-%d %H:%M:%S')
            params = {
                'access_key': API_KEY,
                'currencies': 'AED,ALL,AMD,ANG,ARS,AUD, RUB',
                'date': formatted_date
            }

            response = requests.get(base_url, params=params)
            data = response.json()

            if 'quotes' in data:
                quotes = data['quotes']
                bot.send_message(call.message.chat.id, f'Актуальные данные о валютах на {formatted_date}')
                time.sleep(1)
                for currency, rate in quotes.items():
                    bot.send_message(call.message.chat.id, f'1 USD = {rate} {currency[3:]}')  # Выводим курс относительно доллара для каждой валюты
            else:
                logging.error(f'Error when receiving currency data')
        except Exception as e:
            logging.error(f'Error occurred while processing info callback: {e}')

        bot.register_next_step_handler(call.message, button)
    else:
        bot.send_message(call.message.chat.id, f'Введите пару значений  через /. Пример usd/rub')
        bot.register_next_step_handler(call.message, check)


def check(message):
    try:
        val = message.text.upper().split('/')
        url = f'http://api.currencylayer.com/convert?access_key=b1b1ec62288ce24ef2c336d60c4f9cef&from={val[0]}&to={val[1]}&amount={cash}'
        response = requests.get(url)
        data = response.json()
        rate = data['result']
        bot.send_message(message.chat.id, f'Перевел {cash} {val[0]} в {round(rate, 2)} {val[1]}')
        logging.info(f'Converted {cash} {val[0]} to {round(rate, 2)} {val[1]}')
        bot.register_next_step_handler(message, button)
    except Exception as e:
        logging.error(f'Error occurred in check function: {e}')
        bot.register_next_step_handler(message, button)


bot.polling()