import random
import time
from multiprocessing import Process
from telebot import TeleBot, types

import messages
from filehandler import FileHandler
from settings import BOT_TOKEN
from weather import Weather

bot = TeleBot(BOT_TOKEN)

giftImg = "static/coin.png"
greetingImg = "static/pandora-min.png"

commands = {  # command description used in the "help" command
    'start': 'Get used to the bot',
    'help': 'Gives you information about the available commands',
    'whatWeather': 'Show weather from all the world',
    'randomNumber': 'Play game guess a random number'
}


def send_user_weather():
    file_handler = FileHandler()
    users = file_handler.get_users()
    weather = Weather()
    if users:
        users_list = list(users.values())
        for user in users_list:
            try:
                if 'location' in user:
                    weather_message = weather.get_weather_message(user['location'])
                    if weather_message['success']:
                        message_handler(bot, int(user['chatId']), weather_message['message'], parse_mode='html')
            except Exception as exception:
                print(repr(exception))


@bot.message_handler(commands=['start'])
def welcome(message):
    file_handler = FileHandler()
    greeting_sticker = open(greetingImg, 'rb')
    bot.send_sticker(message.chat.id, greeting_sticker)
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(messages.random_btn)
    item_weather = types.KeyboardButton(messages.weather_btn)
    markup.add(item1, item_weather)

    chat_id = message.chat.id
    bot_name = bot.get_me().first_name
    user_name = message.from_user.first_name
    mes = messages.greeting.format(user_name, bot_name)
    file_handler.save_user(message.from_user, chat_id)

    message_handler(bot, chat_id, mes, parse_mode='html', reply_markup=markup)


# help page
@bot.message_handler(commands=['help'])
def command_help(message):
    help_text = messages.commands_list
    for key, value in commands.items():
        help_text += "/" + key + ": "
        help_text += value + "\n"
    message_handler(bot, message.chat.id, help_text)


@bot.message_handler(commands=['whatWeather'])
def command_help(message):
    input_city(message, messages.which_city)


@bot.message_handler(commands=['randomNumber'])
def command_help(message):
    play_random_game(message)


@bot.message_handler(content_types=['text'])
def send(message):
    if message.chat.type == 'private':
        if message.text == messages.random_btn:
            play_random_game(message)
        elif message.text == messages.weather_btn:
            input_city(message, messages.which_city)
        else:
            message_handler(bot, message.chat.id, messages.no_command)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == messages.no_mess:
                random_play = random.randint(0, 1)
                if bool(random_play):
                    markup = types.InlineKeyboardMarkup(row_width=3)
                    item1 = types.InlineKeyboardButton(messages.yes, callback_data=messages.yes_play)
                    item2 = types.InlineKeyboardButton(messages.no, callback_data=messages.no_play)
                    markup.add(item1, item2)

                    message_handler(bot, call.message.chat.id, messages.play_with_me, reply_markup=markup)
            elif call.data == messages.yes_mess:
                input_city(call.message, messages.which_city)
            elif call.data == messages.yes_play:
                play_random_game(call.message)
            elif call.data == messages.yes_again:
                start_game(call.message)
            elif call.data == messages.no_play:
                message_handler(bot, call.message.chat.id, messages.as_wish)
            elif call.data == messages.cancel_step:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Canceled')
                bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)

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
    weather_message = weather.get_weather_message(city, message.from_user.id)
    if weather_message['success']:
        markup = types.InlineKeyboardMarkup(row_width=3)
        item1 = types.InlineKeyboardButton(messages.yes, callback_data=messages.yes_mess)
        item2 = types.InlineKeyboardButton(messages.no, callback_data=messages.no_mess)
        markup.add(item1, item2)

        message_handler(bot, message.chat.id, weather_message['message'], reply_markup=markup, parse_mode='html')
    else:
        input_city(message, weather_message['message'])


def input_city(message, text_mes):
    board = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(text=messages.cancel_step, callback_data=messages.cancel_step)
    board.add(cancel)

    sent = message_handler(bot, message.chat.id, text_mes, reply_markup=board)
    bot.register_next_step_handler(sent, get_weather_message)


def play_random_game(message):
    message_handler(bot, message.chat.id, messages.game_rule)
    start_game(message)


def start_game(message):
    sent = message_handler(bot, message.chat.id, messages.what_number)
    bot.register_next_step_handler(sent, generate_number)


def generate_number(message):
    try:
        rand_number = random.randint(1, 5)
        type_number = int(message.text)
        if type_number == rand_number:
            message_handler(bot, message.chat.id, messages.correct)
            sti = open(giftImg, 'rb')
            bot.send_sticker(message.chat.id, sti)
        else:
            message_handler(bot, message.chat.id, messages.not_correct.format(str(rand_number)), parse_mode='html')

        markup = types.InlineKeyboardMarkup(row_width=3)
        item1 = types.InlineKeyboardButton(messages.yes, callback_data=messages.yes_again)
        item2 = types.InlineKeyboardButton(messages.no, callback_data=messages.no_play)
        markup.add(item1, item2)
    except ValueError:
        sent = message_handler(bot, message.chat.id, messages.not_number)
        bot.register_next_step_handler(sent, generate_number)
    else:
        message_handler(bot, message.chat.id, messages.play_again, reply_markup=markup)


def message_handler(my_bot: TeleBot, chat_id: int, text: str, reply_markup=None, parse_mode=None):
    try:
        return my_bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=reply_markup, )
    except:
        my_bot.send_message(chat_id, messages.something_wrong)


def check_send_messages():
    while True:
        hour, min = map(int, time.strftime("%H %M").split())
        hour = 11
        min = 0
        if (hour == 11 or hour == 15 or hour == 19 or hour == 23) and min == 0:
            send_user_weather()
        time.sleep(60)


if __name__ == '__main__':
    while True:
        try:
            p1 = Process(target=check_send_messages, args=())
            p1.start()

            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(15)
