import telebot
import random
import messages

from weather import Weather
from config import TG_TOKEN
from telebot import types

bot = telebot.TeleBot(TG_TOKEN)

giftImg = "static/coin.png"
greetingImg = "static/pandora-min.png"


@bot.message_handler(commands=['start'])
def welcome(message):
    greeting_sticker = open(greetingImg, 'rb')
    bot.send_sticker(message.chat.id, greeting_sticker)

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(messages.random_btn)
    item_weather = types.KeyboardButton(messages.weather_btn)
    markup.add(item1, item_weather)

    bot_name = bot.get_me().first_name
    user_name = message.from_user.first_name
    mes = messages.greeting.format(user_name, bot_name)

    bot.send_message(message.chat.id, mes, parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def send(message):
    if message.chat.type == 'private':
        if message.text == messages.random_btn:
            play_random_game(message)
        elif message.text == messages.weather_btn:
            input_city(message, messages.which_city)
        else:
            bot.send_message(message.chat.id, messages.no_command)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == messages.no_mess:
                markup = types.InlineKeyboardMarkup(row_width=3)
                item1 = types.InlineKeyboardButton(messages.yes, callback_data=messages.yes_play)
                item2 = types.InlineKeyboardButton(messages.no, callback_data=messages.no_play)

                markup.add(item1, item2)
                bot.send_message(call.message.chat.id, messages.play_with_me, reply_markup=markup)
            elif call.data == messages.yes_mess:
                input_city(call.message, messages.which_city)
            elif call.data == messages.yes_play:
                play_random_game(call.message)
            elif call.data == messages.yes_again:
                start_game(call.message)
            elif call.data == messages.no_play:
                bot.send_message(call.message.chat.id, messages.as_wish)

            # remove inline buttons
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='ok', reply_markup=None)
            # show alert
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text=messages.understand)

    except Exception as e:
        print(repr(e))


@bot.message_handler(func=lambda message: True)
def get_weather_message(message):
    city = message.text
    weather = Weather()
    weather_message = weather.get_weather_message(city)
    if weather_message['success']:
        markup = types.InlineKeyboardMarkup(row_width=3)
        item1 = types.InlineKeyboardButton(messages.yes, callback_data=messages.yes_mess)
        item2 = types.InlineKeyboardButton(messages.no, callback_data=messages.no_mess)
        markup.add(item1, item2)

        bot.send_message(message.chat.id, weather_message['message'], reply_markup=markup, parse_mode='html')
    else:
        input_city(message, weather_message['message'])


def input_city(message, text_mes):
    sent = bot.send_message(message.chat.id, text_mes)
    bot.register_next_step_handler(sent, get_weather_message)


def play_random_game(message):
    bot.send_message(message.chat.id, messages.game_rule)
    start_game(message)


def start_game(message):
    sent = bot.send_message(message.chat.id, messages.what_number)
    bot.register_next_step_handler(sent, generate_number)


def generate_number(message):
    rand_number = random.randint(1, 5)
    if int(message.text) == rand_number:
        bot.send_message(message.chat.id, messages.correct)
        sti = open(giftImg, 'rb')
        bot.send_sticker(message.chat.id, sti)
    else:
        bot.send_message(message.chat.id, messages.not_correct.format(str(rand_number)), parse_mode='html')

    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton(messages.yes, callback_data=messages.yes_again)
    item2 = types.InlineKeyboardButton(messages.no, callback_data=messages.no_play)
    markup.add(item1, item2)

    bot.send_message(message.chat.id, messages.play_again, reply_markup=markup)


# RUN
bot.polling(none_stop=True)
