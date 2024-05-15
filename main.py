import schedule
import telebot
import sqlite3
from telebot import types
import time
from openai import OpenAI
import threading


# Создаем объект бота
bot = telebot.TeleBot('6397841129:AAGaEv9jOOO4ImhKunybjRlmacqGHMiAHdI')

# Подключаемся к базе данных SQLite или создаем ее, если она еще не создана
conn = sqlite3.connect('users.sql')
cursor = conn.cursor()

# Создаем таблицу для хранения информации о пользователях, если она еще не создана
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  chat_id INTEGER UNIQUE, 
                  username TEXT UNIQUE, 
                  password TEXT, 
                  balance REAL)''')

conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS loans
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  chat_id INTEGER UNIQUE, 
                  loan_amount REAL)''')

conn.commit()


# Обработчик команды /start

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    try:
        # Проверяем, зарегистрирован ли пользователь
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
            user = cursor.fetchone()
            if user:
                # Если пользователь зарегистрирован, формируем клавиатуру со всеми функциями
                markup = types.ReplyKeyboardMarkup(row_width=2)
                itembtn1 = types.KeyboardButton('Профиль👤')
                itembtn2 = types.KeyboardButton('Баланс💰')
                itembtn3 = types.KeyboardButton('Пополнение💸')
                itembtn4 = types.KeyboardButton('Транзакция🔀')
                itembtn5 = types.KeyboardButton('Оформить кредит💳')
                itembtn6 = types.KeyboardButton('Погашение кредита💳')
                itembtn7 = types.KeyboardButton('Изменить данные✏️')
                itembtn8 = types.KeyboardButton('Удалить учетную запись🗑️')
                itembtn9 = types.KeyboardButton('Помощь🆘')
                itembtn10 = types.KeyboardButton('Магазин🛒')
                markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9,itembtn10)
                bot.reply_to(message, "Выберите действие:", reply_markup=markup)
            else:
                # Если пользователь не зарегистрирован, предложим ему зарегистрироваться
                markup = types.ReplyKeyboardMarkup(row_width=1)
                itembtn1 = types.KeyboardButton('Регистрация')
                markup.add(itembtn1)
                bot.reply_to(message, "Добро пожаловать! Зарегистрируйтесь, чтобы начать пользоваться нашим сервисом.", reply_markup=markup)
    except sqlite3.Error as e:
        print("Ошибка при выполнении SQL-запроса:", e)
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз.")

@bot.message_handler(func=lambda message: message.text == 'Магазин🛒')
def show_store(message):
    # Формируем клавиатуру с товарами
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Товар 1 - 100 рублей')
    itembtn2 = types.KeyboardButton('Товар 2 - 200 рублей')
    itembtn3 = types.KeyboardButton('Товар 3 - 300 рублей')
    markup.add(itembtn1, itembtn2, itembtn3)

    bot.reply_to(message, "Выберите товар:", reply_markup=markup)


# Обработчик для кнопки "Завершить покупку")


# Обработчик для кнопки "Товар"
# Обработчик для кнопки "Товар"

# Обработчик для возврата к выбору товара
# Функция для отображения клавиатуры с товарами
# Список товаров
items = ['Товар 1 - 100 рублей', 'Товар 2 - 150 рублей', 'Товар 3 - 200 рублей']

def show_items(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    for item in items:
        markup.add(types.KeyboardButton(item))
    markup.add(types.KeyboardButton('Завершить покупку'))  # Добавляем кнопку "Завершить покупку"
    bot.reply_to(message, "Выберите товар:", reply_markup=markup)

# Обработчик для кнопки "Товар"
@bot.message_handler(func=lambda message: message.text in items)
def buy_item(message):
    chat_id = message.chat.id
    item_price = int(message.text.split('-')[-1].strip().split()[0])  # Получаем цену товара
    try:
        # Получаем информацию о пользователе из базы данных
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE chat_id=?", (chat_id,))
            user = cursor.fetchone()
            if user:
                user_balance = user[0]
                # Формируем клавиатуру с вариантами выбора оплаты
                markup = types.ReplyKeyboardMarkup(row_width=2)
                itembtn1 = types.KeyboardButton('В кредит')
                itembtn2 = types.KeyboardButton('Просто покупка')
                markup.add(itembtn1, itembtn2)
                bot.reply_to(message, f"Выберите способ оплаты. Цена товара: {item_price} руб.", reply_markup=markup)
                # Сохраняем информацию о товаре в состояние пользователя
                bot.register_next_step_handler(message, lambda m: handle_payment_method(m, chat_id, item_price))
            else:
                bot.reply_to(message, "Вы еще не зарегистрированы.")
    except Exception as e:
        print("Ошибка при обработке покупки:", e)
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз.")

# Обработчик для кнопки "Завершить покупку"
@bot.message_handler(func=lambda message: message.text == 'Завершить покупку')
def finish_purchase(message):
    chat_id = message.chat.id
    show_items(message)  # Вызываем функцию для отображения клавиатуры с товарами

# Обработчик для выбора способа оплаты
def handle_payment_method(message, chat_id, item_price):
    payment_method = message.text.lower()
    if payment_method == 'в кредит':
        # Обрабатываем покупку в кредит
        handle_credit_purchase(message, chat_id, item_price)
    elif payment_method == 'просто покупка':
        # Обрабатываем простую покупку
        handle_regular_purchase(message, chat_id, item_price)
    elif payment_method == 'завершить покупку':
        # Возвращаем основную клавиатуру
        finish_purchase(message)
    else:
        bot.reply_to(message, "Пожалуйста, выберите один из предложенных вариантов.")

# Обработчик для покупки в кредит
def handle_credit_purchase(message, chat_id, item_price):
    try:
        # Рассчитываем цену товара с учетом кредита
        item_price_credit = round(item_price * 1.025, 2)
        # Получаем информацию о пользователе из базы данных
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT loan_amount FROM loans WHERE chat_id=?", (chat_id,))
            loans = cursor.fetchall()
            total_loan_amount = sum(loan[0] for loan in loans)
            new_loan_amount = total_loan_amount + item_price_credit
            # Обновляем информацию о кредите пользователя
            cursor.execute("INSERT INTO loans (chat_id, loan_amount) VALUES (?, ?)", (chat_id, new_loan_amount))
            conn.commit()
            bot.reply_to(message, f"Покупка в кредит совершена. Ваш текущий кредит: {new_loan_amount} руб.")
    except sqlite3.Error as e:
        print("Ошибка при обработке покупки в кредит:", e)
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз.")

# Обработчик для обычной покупки
def handle_regular_purchase(message, chat_id, item_price):
    markup = create_main_keyboard()
    try:
        # Получаем информацию о пользователе из базы данных
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE chat_id=?", (chat_id,))
            user = cursor.fetchone()
            if user:
                user_balance = user[0]
                if user_balance >= item_price:
                    # Обновляем баланс пользователя
                    new_balance = user_balance - item_price
                    cursor.execute("UPDATE users SET balance=? WHERE chat_id=?", (new_balance, chat_id))
                    conn.commit()
                    bot.reply_to(message, f"Простая покупка совершена. Остаток на вашем балансе: {new_balance} руб.", reply_markup = markup)
                else:
                    bot.reply_to(message, "Недостаточно средств на балансе.", reply_markup = markup)
    except sqlite3.Error as e:
        print("Ошибка при обработке обычной покупки:", e)
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз.", reply_markup = markup)

@bot.message_handler(func=lambda message: message.text == 'Помощь🆘')
def help(message):
    # Формируем сообщение с часто задаваемыми вопросами и ответами
    faq_message = '''
        Вот некоторые часто задаваемые вопросы и ответы:

        1. Как зарегистрироваться?
           - Ответ: Для регистрации нажмите кнопку "Регистрация" или отправьте команду /register.

        2. Как узнать свой текущий баланс?
           - Ответ: Для просмотра баланса нажмите кнопку "Баланс" или отправьте команду /balance.

        3. Как пополнить баланс?
           - Ответ: Для пополнения баланса нажмите кнопку "Пополнение" или отправьте команду /topup, а затем следуйте инструкциям.

        4. Как совершить транзакцию?
           - Ответ: Для совершения транзакции нажмите кнопку "Транзакция" или отправьте команду /transaction, а затем следуйте инструкциям.

        5. Как оформить кредит?
           - Ответ: Для оформления кредита нажмите кнопку "Оформить кредит" или отправьте команду /loan, а затем следуйте инструкциям.

        6. Как погасить кредит?
           - Ответ: Для погашения кредита нажмите кнопку "Погашение кредита" или отправьте команду /repay_loan, а затем следуйте инструкциям.

        7. Как изменить свои данные?
           - Ответ: Для изменения своих данных нажмите кнопку "Изменить данные" или отправьте команду /edit_profile, а затем следуйте инструкциям.

        8. Как удалить свою учетную запись?
           - Ответ: Для удаления своей учетной записи нажмите кнопку "Удалить учетную запись" или отправьте команду /delete_account.

        9. Как получить помощь или связаться с поддержкой?
           - Ответ: Для получения помощи или связи с поддержкой отправьте сообщение с вашим вопросом или проблемой. Мы постараемся ответить как можно скорее.
        '''
    # Отправляем сообщение с часто задаваемыми вопросами и ответами
    bot.reply_to(message, faq_message)


@bot.message_handler(func=lambda message: message.text == 'Удалить учетную запись🗑️')
def delete_account(message):
    chat_id = message.chat.id
    try:
        # Проверяем, есть ли у пользователя кредитная задолженность
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT loan_amount FROM loans WHERE chat_id=?", (chat_id,))
            loan = cursor.fetchone()
            if loan:
                bot.reply_to(message, "Нельзя удалить учетную запись, пока есть задолженность по кредиту.")
                return  # Прерываем выполнение функции, чтобы не удалять учетную запись

        # После запроса подтверждения удаления, отображаем кнопки "Подтвердить" и "Отменить"
        markup = types.ReplyKeyboardMarkup(row_width=2)
        confirm_button = types.KeyboardButton('Подтвердить')
        cancel_button = types.KeyboardButton('Отменить')
        markup.add(confirm_button, cancel_button)
        bot.send_message(chat_id, "Вы уверены, что хотите удалить учетную запись?", reply_markup=markup)
    except sqlite3.Error as e:
        print("Ошибка при удалении учетной записи:", e)
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз.")


# Обрабатываем нажатие кнопки "Подтвердить"
@bot.message_handler(func=lambda message: message.text == 'Подтвердить')
def confirm_delete(message):
    chat_id = message.chat.id
    try:
        # Удаляем учетную запись пользователя из базы данных
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE chat_id=?", (chat_id,))
            conn.commit()

        # Проверяем, существует ли чат
        chat_exists = bot.get_chat(chat_id)
        if chat_exists:
            bot.reply_to(message, "Ваша учетная запись успешно удалена.")
            # После удаления учетной записи убираем все кнопки и добавляем кнопку для регистрации
            markup = types.ReplyKeyboardMarkup(row_width=1)
            itembtn1 = types.KeyboardButton('Регистрация')
            markup.add(itembtn1)
            bot.send_message(chat_id, "Ваша учетная запись удалена. Пожалуйста, зарегистрируйтесь заново.",
                             reply_markup=markup)
    except sqlite3.Error as e:
        print("Ошибка при удалении учетной записи:", e)
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз.")


# Обрабатываем нажатие кнопки "Отменить"
# Обрабатываем нажатие кнопки "Отменить"
@bot.message_handler(func=lambda message: message.text == 'Отменить')
def cancel_delete(message):
    chat_id = message.chat.id
    try:
        # Возвращаем исходные кнопки
        markup = create_main_keyboard()
        bot.send_message(chat_id, "Удаление учетной записи отменено.", reply_markup=markup)
    except Exception as e:
        print("Ошибка при отмене удаления учетной записи:", e)
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз.")

def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Профиль👤')
    itembtn2 = types.KeyboardButton('Баланс💰')
    itembtn3 = types.KeyboardButton('Пополнение💸')
    itembtn4 = types.KeyboardButton('Транзакция🔀')
    itembtn5 = types.KeyboardButton('Оформить кредит💳')
    itembtn6 = types.KeyboardButton('Погашение кредита💳')
    itembtn7 = types.KeyboardButton('Изменить данные✏️')
    itembtn10 = types.KeyboardButton('Магазин🛒')
    itembtn8 = types.KeyboardButton('Удалить учетную запись🗑️')

    itembtn9 = types.KeyboardButton('Помощь🆘')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9,itembtn10)
    return markup


@bot.message_handler(func=lambda message: message.text == 'Изменить данные✏️')
def change_personal_data(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Какие данные вы хотите изменить? (Напишите 'имя', или 'пароль'):")
    bot.register_next_step_handler(message, process_change_data)

def process_change_data(message):
    chat_id = message.chat.id
    data_to_change = message.text.lower()
    if data_to_change in ['имя', 'фамилия', 'пароль']:
        bot.send_message(chat_id, f"Введите новое значение для {data_to_change}:")
        bot.register_next_step_handler(message, lambda m: save_new_data(chat_id, data_to_change, m.text))
    else:
        bot.send_message(chat_id, "Пожалуйста, выберите 'имя', 'фамилия' или 'пароль' для изменения.")

def save_new_data(chat_id, data_to_change, new_value):
    try:
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            if data_to_change == 'имя':
                cursor.execute("UPDATE users SET username=? WHERE chat_id=?", (new_value, chat_id))
            elif data_to_change == 'фамилия':
                cursor.execute("UPDATE users SET surname=? WHERE chat_id=?", (new_value, chat_id))
            elif data_to_change == 'пароль':
                cursor.execute("UPDATE users SET password=? WHERE chat_id=?", (new_value, chat_id))
            conn.commit()
            bot.send_message(chat_id, f"Данные успешно изменены: {data_to_change} -> {new_value}")
    except Exception as e:
        print("Ошибка при изменении данных:", e)
        bot.send_message(chat_id, "Произошла ошибка при изменении данных. Пожалуйста, попробуйте еще раз.")




# Обработчик команды Оформить кредит
# Обработчик команды Оформить кредит
@bot.message_handler(func=lambda message: message.text == 'Оформить кредит💳')
def apply_for_loan(message):
    chat_id = message.chat.id
    try:
        # Проверяем, есть ли у пользователя активный кредит
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM loans WHERE chat_id=?", (chat_id,))
            existing_loan = cursor.fetchone()
            if existing_loan:
                bot.reply_to(message, "У вас уже есть активный кредит. Пожалуйста, погасите его, прежде чем брать новый.")
            else:
                bot.reply_to(message, "Введите сумму кредита:")
                bot.register_next_step_handler(message, process_loan_application)
    except Exception as e:
        print("Ошибка при оформлении кредита:", e)

# Функция для обработки заявки на кредит
# Функция для обработки заявки на кредит
def process_loan_application(message):
    chat_id = message.chat.id
    try:
        loan_amount = float(message.text)
        if loan_amount > 0:
            interest_rate = 2.5 / 100
            interest_amount = loan_amount * interest_rate
            total_amount_due = loan_amount + interest_amount
            # Сохраняем информацию о кредите в базе данных
            with sqlite3.connect('users.sql') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO loans (chat_id, loan_amount) VALUES (?, ?)", (chat_id, loan_amount))
                conn.commit()

            # Отправляем пользователю информацию о кредите и клавиатуру для подтверждения или отмены
            markup = types.InlineKeyboardMarkup(row_width=2)
            confirm_button = types.InlineKeyboardButton("Подтвердить", callback_data=f"confirm_loan_{loan_amount}")
            cancel_button = types.InlineKeyboardButton("Отменить", callback_data="cancel_loan")
            markup.add(confirm_button, cancel_button)
            bot.send_message(chat_id,f"Сумма кредита: {loan_amount} руб.\nПроценты по кредиту: {interest_amount} руб.\nИтого к возврату: {total_amount_due} руб.\n\nПодтвердите вашу заявку на кредит:",
                             reply_markup=markup)
        else:
            bot.reply_to(message, "Сумма кредита должна быть положительной.")
    except ValueError:
        bot.reply_to(message, "Неверный формат суммы. Пожалуйста, введите сумму кредита числом.")


# Обработчик нажатия на кнопку подтверждения кредита
# Обработчик нажатия на кнопку подтверждения кредита
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_loan_'))
def confirm_loan(call):
    try:
        chat_id = call.message.chat.id
        total_amount_due = float(call.data.split('_')[-1])

        # Получаем текущий баланс пользователя
        current_balance = 0
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE chat_id = ?", (chat_id,))
            row = cursor.fetchone()
            if row:
                current_balance = row[0]

        # Обновляем баланс пользователя (прибавляем сумму кредита)
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET balance = ? WHERE chat_id = ?",
                           (current_balance + total_amount_due, chat_id))
            conn.commit()

        bot.send_message(chat_id,
                         f"Кредит успешно одобрен. Ваш текущий баланс: {current_balance + total_amount_due} руб.")
    except Exception as e:
        print("Ошибка при подтверждении кредита:", e)


# Обработчик нажатия на кнопку отмены кредита
@bot.callback_query_handler(func=lambda call: call.data == 'cancel_loan')
def cancel_loan(call):
    try:
        chat_id = call.message.chat.id
        bot.send_message(chat_id, "Заявка на кредит отменена.")
    except Exception as e:
        print("Ошибка при отмене кредита:", e)

# Запуск бота

# Обработчик команды Погашение кредита
# Обработчик команды Погашение кредита
@bot.message_handler(func=lambda message: message.text == 'Погашение кредита💳')
def repay_loan(message):
    chat_id = message.chat.id
    try:
        # Получаем информацию о пользователе из базы данных
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE chat_id=?", (chat_id,))
            user = cursor.fetchone()
            if user:
                # Проверяем, есть ли у пользователя кредитные задолженности
                cursor.execute("SELECT loan_amount FROM loans WHERE chat_id=?", (chat_id,))
                loan = cursor.fetchone()
                if loan:
                    # Если есть, получаем сумму задолженности (с учетом процентов)
                    debt = calculate_loan_debt(chat_id)
                    bot.reply_to(message, f"Общая сумма задолженности: {debt} руб.\nВведите сумму, которую вы готовы внести сейчас:")
                    bot.register_next_step_handler(message, process_repayment)
                else:
                    bot.reply_to(message, "У вас нет задолженностей по кредиту.")
            else:
                bot.reply_to(message, "Вы еще не зарегистрированы.")
    except Exception as e:
        print("Ошибка при погашении кредита:", e)


# Функция для расчета суммы задолженности пользователя (с учетом процентов)
def calculate_loan_debt(chat_id):
    try:
        interest_rate = 2.5 / 100
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT loan_amount FROM loans WHERE chat_id=?", (chat_id,))
            loan_amount = cursor.fetchone()
            if loan_amount:
                loan_amount = loan_amount[0]
                interest_amount = loan_amount * interest_rate
                total_amount_due = loan_amount + interest_amount
                return total_amount_due
            else:
                return 0
    except Exception as e:
        print("Ошибка при расчете задолженности по кредиту:", e)
        return 0

def calculate_loan_debt2(chat_id):
    try:
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT loan_amount FROM loans WHERE chat_id=?", (chat_id,))
            loan_amount = cursor.fetchone()
            if loan_amount:
                return loan_amount[0]
            else:
                return 0
    except Exception as e:
        print("Ошибка при расчете задолженности по кредиту:", e)
        return 0



# Функция для отправки уведомления о задолженности


# Функция для отправки уведомления о задолженности


# Функция для проверки задолженности и отправки уведомления



# Функция для отправки уведомления о задолженности
def send_loan_notification(chat_id):
    while True:
        try:
            debt = calculate_loan_debt(chat_id)
            if debt > 0:
                bot.send_message(chat_id,
                                 f"У вас есть задолженность по кредиту в размере {debt} руб. Пожалуйста, погасите ее как можно скорее.")
        except Exception as e:
            print("Ошибка при отправке уведомления о задолженности:", e)

        # Пауза на одну минуту перед следующей проверкой
        time.sleep(60)


# Создаем и запускаем поток для отправки уведомлений
chat_id = 1415990319  # Замените на нужный вам chat_id
notification_thread = threading.Thread(target=send_loan_notification, args=(chat_id,))
notification_thread.daemon = True  # Устанавливаем фоновый режим потока
notification_thread.start()


# Запуск функции для проверки задолженности и отправки уведомлений
  # Замените на нужный вам chat_id


# Функция для обработки погашения кредита

# Функция для обработки погашения кредита
def process_repayment(message):
    chat_id = message.chat.id
    try:
        amount = float(message.text)
        if amount > 0:
            debt = calculate_loan_debt(chat_id)
            if amount <= debt:
                # Получаем текущий баланс пользователя
                current_balance = get_user_balance(chat_id)
                if current_balance >= amount:
                    # Обновляем баланс пользователя после погашения кредита
                    update_user_balance(chat_id, current_balance - amount)

                    # Обновляем сумму задолженности
                    new_debt = debt - amount
                    update_loan_debt(chat_id, new_debt)

                    if new_debt > 0:
                        bot.reply_to(message, f"Вы успешно погасили {amount} руб. Остаток задолженности: {new_debt:.2f} руб.")
                    else:
                        # Если задолженность погашена полностью, удаляем запись о кредите из базы данных
                        with sqlite3.connect('users.sql') as conn:
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM loans WHERE chat_id=?", (chat_id,))
                            conn.commit()
                        bot.reply_to(message, "Вы успешно погасили кредит. Задолженность полностью погашена.")
                else:
                    bot.reply_to(message, "Недостаточно средств на вашем счете для погашения кредита.")
            else:
                bot.reply_to(message, f"Сумма погашения не может превышать общей суммы задолженности ({debt} руб.).")
        else:
            bot.reply_to(message, "Сумма погашения должна быть положительной.")
    except ValueError:
        bot.reply_to(message, "Неверный формат суммы. Пожалуйста, введите сумму числом.")
    except Exception as e:
        print("Ошибка при погашении кредита:", e)






def update_loan_debt(chat_id, new_debt):
    try:
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE loans SET loan_amount=? WHERE chat_id=?", (new_debt, chat_id))
            conn.commit()
    except Exception as e:
        print("Ошибка при обновлении суммы задолженности:", e)



# Функция для получения текущего баланса пользователя
def get_user_balance(chat_id):
    with sqlite3.connect('users.sql') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE chat_id=?", (chat_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            return 0


# Функция для обновления баланса пользователя
def update_user_balance(chat_id, new_balance):
    with sqlite3.connect('users.sql') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance=? WHERE chat_id=?", (new_balance, chat_id))
        conn.commit()


# Обработчик команды /profile


@bot.message_handler(func=lambda message: message.text == 'Профиль👤')
def view_profile(message):
    chat_id = message.chat.id
    try:
        # Получаем информацию о пользователе
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
            user = cursor.fetchone()
            if user:
                username, password, balance = user[2], user[3], user[4]

                # Создание клавиатуры с кнопкой "Показать пароль"
                keyboard = types.InlineKeyboardMarkup()
                show_button = types.InlineKeyboardButton(text="Показать пароль", callback_data="show_password")
                keyboard.add(show_button)

                # Формирование сообщения с скрытым паролем и клавиатурой
                response = f"Имя: {username}\nПароль: *********\nБаланс: {balance} руб."
                bot.reply_to(message, response, reply_markup=keyboard)
            else:
                bot.reply_to(message, "Пользователь не найден.")
    except sqlite3.Error as e:
        print("Ошибка при выполнении SQL-запроса:", e)
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз.")


@bot.callback_query_handler(func=lambda call: call.data == "show_password")
def show_password(call):
    chat_id = call.message.chat.id
    try:
        # Получаем информацию о пользователе
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE chat_id=?", (chat_id,))
            user_password = cursor.fetchone()[0]

            # Отправляем сообщение с отображением пароля
            bot.send_message(chat_id, f"Ваш пароль: {user_password}")
    except sqlite3.Error as e:
        print("Ошибка при выполнении SQL-запроса:", e)
        bot.send_message(chat_id, "Произошла ошибка. Пожалуйста, попробуйте еще раз.")


# Обработчик команды /balance
@bot.message_handler(func=lambda message: message.text == 'Баланс💰')
def check_balance(message):
    chat_id = message.chat.id
    try:
        # Создаем новое подключение к базе данных и объект курсора
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE chat_id=?", (chat_id,))
            result = cursor.fetchone()
            if result:
                bot.reply_to(message, f"Ваш текущий баланс: {result[0]} руб.")
            else:
                bot.reply_to(message, "Вы еще не зарегистрированы.")
    except sqlite3.Error as e:
        print("Ошибка при выполнении SQL-запроса:", e)
        bot.reply_to(message, "Произошла ошибка при получении баланса. Пожалуйста, попробуйте еще раз.")

# Обработчик команды /top_up
@bot.message_handler(func=lambda message: message.text == 'Пополнение💸')
def top_up_balance(message):
    bot.reply_to(message, "Введите сумму для пополнения:")
    bot.register_next_step_handler(message, process_top_up)

# Обработчик команды /transfer
@bot.message_handler(func=lambda message: message.text == 'Транзакция🔀')
def transfer_balance(message):
    bot.reply_to(message, "Введите сумму и username получателя через пробел:")
    bot.register_next_step_handler(message, process_transfer)

# Обработчик команды /register
@bot.message_handler(func=lambda message: message.text == 'Регистрация')
def register_user(message):
    bot.reply_to(message, "Введите ваше имя и пароль через пробел:")
    bot.register_next_step_handler(message, process_registration)

# Функция для обработки регистрации пользователя
def process_registration(message):
    chat_id = message.chat.id
    try:
        username, password = message.text.split()
        # Создаем новое подключение к базе данных и объект курсора
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (chat_id, username, password, balance) VALUES (?, ?, ?, ?)",
                           (chat_id, username, password, 0))
            conn.commit()
        bot.reply_to(message, f"Пользователь {username} успешно зарегистрирован.\n Введите /start что бы продолжить")
    except ValueError:
        bot.reply_to(message, "Неверный формат ввода. Пожалуйста, введите ваше имя и пароль через пробел.")
    except sqlite3.Error as e:
        print("Ошибка при выполнении SQL-запроса:", e)
        bot.reply_to(message, "Произошла ошибка при регистрации пользователя. Пожалуйста, попробуйте еще раз.")


# Функция для обработки пополнения счета
def process_top_up(message):
    chat_id = message.chat.id
    try:
        amount = float(message.text)
        if amount > 0:
            # Создаем новый объект курсора и подключаемся к базе данных
            with sqlite3.connect('users.sql') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET balance = balance + ? WHERE chat_id = ?", (amount, chat_id))
                conn.commit()
            bot.reply_to(message, f"Счет успешно пополнен на {amount} руб. Ваш текущий баланс: {amount} руб.")
        else:
            bot.reply_to(message, "Сумма пополнения должна быть положительной.")
    except ValueError:
        bot.reply_to(message, "Неверный формат суммы. Попробуйте снова.")
    except sqlite3.Error as e:
        print("Ошибка при выполнении SQL-запроса:", e)
        bot.reply_to(message, "Произошла ошибка при пополнении счета. Пожалуйста, попробуйте еще раз.")




# Функция для обработки трансфера средств
def process_transfer(message):
    sender_chat_id = message.chat.id
    try:
        # Разделяем сообщение только один раз
        split_message = message.text.split(maxsplit=1)
        amount = float(split_message[0])
        recipient_username = split_message[1].strip()

        # Создаем новое подключение к базе данных и объект курсора
        with sqlite3.connect('users.sql') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM users WHERE username=?", (recipient_username,))
            recipient_chat_id = cursor.fetchone()
            if recipient_chat_id:
                recipient_chat_id = recipient_chat_id[0]
                if amount > 0:
                    cursor.execute("SELECT balance FROM users WHERE chat_id=?", (sender_chat_id,))
                    sender_balance = cursor.fetchone()
                    if sender_balance and sender_balance[0] >= amount:
                        cursor.execute("UPDATE users SET balance = balance - ? WHERE chat_id = ?", (amount, sender_chat_id))
                        cursor.execute("UPDATE users SET balance = balance + ? WHERE chat_id = ?",
                                       (amount, recipient_chat_id))
                        conn.commit()
                        bot.reply_to(message,
                                     f"Транзакция успешно выполнена. С вашего счета списано {amount} руб., пользователю {recipient_username} зачислено {amount} руб.")
                        # Отправляем уведомление получателю о получении денег
                        bot.send_message(recipient_chat_id, f"Вы получили {amount} руб. от пользователя {message.from_user.username}")
                    else:
                        bot.reply_to(message, "Недостаточно средств на счету.")
                else:
                    bot.reply_to(message, "Сумма трансфера должна быть положительной.")
            else:
                bot.reply_to(message, "Пользователь с таким именем не найден.")
    except ValueError:
        bot.reply_to(message, "Неверный формат ввода. Пожалуйста, введите сумму и имя получателя через пробел.")
    except sqlite3.Error as e:
        print("Ошибка при выполнении SQL-запроса:", e)
        bot.reply_to(message, "Произошла ошибка при выполнении транзакции. Пожалуйста, попробуйте еще раз.")


# Запуск бота
bot.polling()
