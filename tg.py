import telebot
import requests
from bs4 import BeautifulSoup
from telebot import types
import re


bot = telebot.TeleBot('7645331493:AAF_6Y9biB_bHmcpCkCT9FpfomRXJ8PN4nI')


def get_product_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    divs = soup.find_all('div', class_=lambda x: x and x.startswith('_title_'))
    if not divs:
        name = "Название товара не найдено"
    else:
        text = divs[0].get_text()
        filtered_text = re.sub(r'[\u4e00-\u9fff]+', '', text)
        print(filtered_text)
        name = filtered_text

    img = soup.find('img')
    if img and 'src' in img.attrs:
        image = img['src']
    else:
        image = "Изображение не найдено"

    price_div = soup.find('div', class_='_itemValue_')
    if price_div:
        price = price_div.get_text()
    else:
        price = "Цена не найдена"

    return name, image, price




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
        name, image, price = get_product_info(message.text)
        if image and image != "Изображение не найдено":
            bot.send_photo(message.from_user.id, image)
        else:
            bot.send_message(message.from_user.id, image)

        bot.send_message(message.from_user.id, f"Название товара: {name}\nЦена: {price}")
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
