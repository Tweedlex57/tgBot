import telebot
import requests
from bs4 import BeautifulSoup
from telebot import types
import re
import sqlite3

bot = telebot.TeleBot('7645331493:AAH9NJnfUdpkszrUrHnGGf64WszB7o6VTUI')
d = 0
c = 0
cny = 0

def create_connection():
    conn = sqlite3.connect('project3.db')
    return conn


def insert_to_cart(user_id, image, name, url):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO deceipt (id_user, url, name, url_order) VALUES (?, ?, ?,?)", (user_id, image, name, url))
    conn.commit()
    conn.close()


def insert_to_cart_size(user_id, size):
    global d
    global cny
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(order_id) FROM deceipt WHERE id_user = ?", (user_id,))
    order_id = cursor.fetchone()[0]

    cursor.execute("UPDATE deceipt SET size = ? WHERE order_id = ?", (size, order_id))

    conn.commit()
    conn.close()
    d = 0
    cny = 1


def insert_to_cart_money(user_id, money):
    global cny
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(order_id) FROM deceipt")
    order_id = cursor.fetchone()[0]

    cursor.execute("UPDATE deceipt SET price = ? WHERE order_id = ?", (money, order_id))
    conn.commit()
    conn.close()
    cny = 0

def order(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(order_id) FROM deceipt WHERE id_user = ?", (user_id,))
    order_id = cursor.fetchone()[0]

    cursor.execute("SELECT name, size, url_order, price, url FROM deceipt WHERE order_id = ?", (order_id,))
    order_data = cursor.fetchone()

    conn.close()
    return order_data


def delet(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(order_id) FROM deceipt WHERE id_user = ?", (user_id,))
    order_id = cursor.fetchone()[0]

    cursor.execute("DELETE FROM deceipt WHERE order_id = ?", (order_id,))
    conn.close()


def deceipt_order(user_id, chat_id):
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Отменить", callback_data="back1")
    safe_button = types.InlineKeyboardButton("Подтвердить", callback_data="next_order")
    markup.add(safe_button, back_button)
    order_data = order(user_id)
    name, size, url, price, image = order_data
    caption = f"🛒 Ваш заказ\n SHOP ✖️ POIZON\n\n"f"⇧ Модель: {name}\n⇧ Размер: {size}\n⇧ Ссылка: {url}\n\n"\
              f"Итоговая стоимость:\n {price} RUB 🔥\n________\nКомиссия сервиса: 1000₽"
    bot.send_photo(chat_id, photo=image, caption=caption, reply_markup=markup)



def get_product_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    divs = soup.find_all('div', class_=lambda x: x and x.startswith('_title_'))
    if not divs:
        name = "Название товара не найдено"
    else:
        text = divs[0].get_text()
        filtered_text = re.sub(r'[\u4e00-\u9fff]+', '', text)
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
    markup = types.InlineKeyboardMarkup()
    order_button = types.InlineKeyboardButton("Сделать заказ", callback_data="order")
    calculator_button = types.InlineKeyboardButton("Калькулятор цены", callback_data="calculator")

    markup.add(order_button).row(calculator_button)
    bot.send_message(chat_id, "Привет! Давай знакомиться👋🏼 \nЯ заботливый бот POIZON_SHOP🔥"
                              "\nЯ помогу тебе рассчитать стоимость товара с площадки POIZON в рублях.", reply_markup=markup)

def calculator(rubles):
    url = 'https://www.cbr.ru/currency_base/daily/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find('table', class_='data')

    if table:
        rows = table.find_all('tr')
        for row in rows[1:]:
            columns = row.find_all('td')
            if columns and 'CNY' in columns[1].get_text():
                cny_rate = columns[4].get_text().replace(',', '.')
                amount_in_rub =  float(cny_rate) * rubles + 1000
                return cny_rate, amount_in_rub


def order_calculator(chat_id):
    global c
    c = 1
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Назад", callback_data="back1")
    markup.add(back_button)

    image_path = '3.jpg'
    caption = 'Выберите размер и напишите актуальную стоимость выбранного товара в ¥ (CNY)'

    with open(image_path, 'rb') as image_file:
        bot.send_photo(chat_id, photo=image_file, caption=caption, reply_markup=markup)

def make_order_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Отменить", callback_data="del")
    markup.add(back_button)

    image_path = '3.jpg'
    caption = 'Шаг 1 из 3: Нажмите на товаре в Poizon кнопку «поделиться».\nСкопируйте ссылку и вставьте сюда.'

    with open(image_path, 'rb') as image_file:
        bot.send_photo(chat_id, photo=image_file, caption=caption, reply_markup=markup)


def make_size_keyboard(chat_id):
    global d
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Отменить", callback_data="del")
    markup.add(back_button)
    d += 1

    image_path = '5.jpg'
    caption = 'Шаг 2 из 3: Выберите размер или доступные параметры товара. Чтобы подобрать правильно, загляните в размерную сетку.'

    with open(image_path, 'rb') as image_file:
        bot.send_photo(chat_id, photo=image_file, caption=caption, reply_markup=markup)


def make_money_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Отменить", callback_data="del")
    next_button = types.InlineKeyboardButton("Продолжить", callback_data="next1")
    markup.add(next_button).row(back_button)

    image_path = '4.jpg'
    caption = 'Шаг 3 из 3: Выберите размер и отправьте цену (в юанях).'

    with open(image_path, 'rb') as image_file:
        bot.send_photo(chat_id, photo=image_file, caption=caption, reply_markup=markup)


def send_back_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Назад", callback_data="back2")
    markup.add(back_button)


@bot.message_handler(commands=['start'])
def start_message(message):
    send_welcome_keyboard(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "order":
        make_order_keyboard(call.message.chat.id)
    elif call.data == "cart":
        bot.send_message(call.message.chat.id, "Ваша корзина пуста.")
    elif call.data == "back1":
        send_welcome_keyboard(call.message.chat.id)
    elif call.data == "back2":
        make_order_keyboard(call.message.chat.id)
    elif call.data == 'calculator':
        order_calculator(call.message.chat.id)
    elif call.data == 'add_to_cart':
        user_id = call.from_user.id
        print(user_id, call.message.text)
        insert_to_cart(user_id, call.message.text)
        send_welcome_keyboard(call.message.chat.id)
    elif call.data == 'back3':
        send_welcome_keyboard(call.message.chat.id)
    elif call.data == 'next1':
        deceipt_order(call.from_user.id, call.message.chat.id)
    elif call.data == 'del':
        delet(call.from_user.id)
        send_welcome_keyboard(call.message.chat.id)
    elif call.data == 'next_order':
        bot.send_message(chat_id, 'С нами свяжется наш менеджер, ожидайте :)')


@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    global c
    global d
    global cny
    if message.text.startswith("http://") or message.text.startswith("https://"):
        name, image, price = get_product_info(message.text)
        url = message.text

        if image and image != "Изображение не найдено":
            user_id = message.from_user.id
            insert_to_cart(user_id, image, name, url)
            markup = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("Отменить", callback_data="back3")
            add_button = types.InlineKeyboardButton("Добавить в корзину", callback_data="add_to_cart")
            markup.add(add_button, back_button)
        else:
            bot.send_message(message.chat.id, 'ОШИБКА! Проверь правильно ссылки)')
        make_size_keyboard(message.chat.id)
    elif d >= 1:
        if message.text.isdigit():
            user_id = message.from_user.id
            size = message.text
            insert_to_cart_size(user_id, size)
        elif message.text== '':
            user_id = message.from_user.id
            size = message.text
            insert_to_cart_size(user_id, size)
        make_money_keyboard(message.chat.id)

    elif cny >= 1:
        if message.text.isdigit():
            rubles = int(message.text)
            user_id = message.from_user.id
            cny_rate, money = calculator(rubles)
            insert_to_cart_money(user_id, int(money))

    elif message.text.isdigit() and c>=1:
        rubles = int(message.text)
        cny_rate, amount_in_rub = calculator(rubles)
        bot.send_message(message.chat.id,
                         f"Итоговая стоимость: {int(amount_in_rub)} RUB 🔥\n____________\nCNY: {rubles} ¥\n"
                         f"Курс CNY: {cny_rate}\nКомиссия сервиса: 1 000 ₽")

bot.polling(none_stop=True, interval=0)