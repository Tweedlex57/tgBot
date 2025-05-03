import telebot
import requests
from bs4 import BeautifulSoup
from telebot import types


bot = telebot.TeleBot('7645331493:AAF_6Y9biB_bHmcpCkCT9FpfomRXJ8PN4nI')


def get_product_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    img = soup.find('img')
    if img and 'src' in img.attrs:
        image = img['src']
    else:
        image = "Изображение не найдено"
    return image


def send_welcome_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    order_button = types.KeyboardButton("Сделать заказ")
    check_product_button = types.KeyboardButton("Проверить товар")
    cart_button = types.KeyboardButton("Корзина")

    markup.add(order_button, check_product_button, cart_button)
    bot.send_message(chat_id, "Привет! Выберите действие:", reply_markup=markup)

def send_make_an_order_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    help_button = types.KeyboardButton("Откуда брать ссылку?")
    back_button = types.KeyboardButton("Назад")

    markup.add(help_button, back_button)

    bot.send_message(chat_id, "Сделайте свой выбор:", reply_markup=markup)

def send_checking_the_orders_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton("Назад")
    markup.add(back_button)
    bot.send_message(chat_id, "Скиньте id товара:", reply_markup=markup)

def send_back_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton("Назад")
    markup.add(back_button)
    bot.send_message(chat_id, "Из сообщения выберете именно ссылку и отправьте мне её!", reply_markup=markup)


@bot.message_handler(commands=['start'])
def start_message(message):
    send_welcome_keyboard(message.from_user.id)

c = 0

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global c
    user_message = message.text.lower()

    if user_message == "привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
        send_welcome_keyboard(message.from_user.id)
    elif user_message == "/help":
        send_welcome_keyboard(message.from_user.id)
    elif user_message == "проверить товар":
        send_checking_the_orders_keyboard(message.from_user.id)
    elif user_message == "сделать заказ":
        send_make_an_order_keyboard(message.from_user.id)
        c = 1
    elif message.text.startswith("http://") or message.text.startswith("https://") and c == 1:
        image = get_product_info(message.text)
        if image:
            if image != "Изображение не найдено":
                bot.send_photo(message.from_user.id, image)
            else:
                bot.send_message(message.from_user.id, image)
        else:
            bot.send_message(message.from_user.id, "Не удалось извлечь информацию о товаре.")
        c = 0
    elif user_message == 'откуда брать ссылку?':
        image = ['1.jpg', '2.jpg']
        images = [types.InputMedia(type='photo', media=types.InputFile(i)) for i in image]

        bot.send_media_group(message.from_user.id, media=images)
        send_back_keyboard(message.from_user.id)
    elif user_message == 'назад':
        send_welcome_keyboard(message.from_user.id)
    elif user_message == "корзина":
        bot.send_message(message.from_user.id, "Ваша корзина пуста.")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

bot.polling(none_stop=True, interval=0)
