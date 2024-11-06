import telebot
import sqlite3
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import os

# Инициализация бота с токеном
TOKEN = os.getenv('7896430421:AAExd1DmhC6dcK0ms5W6q9AmDKF90C4knLQ')
bot = telebot.TeleBot('7896430421:AAExd1DmhC6dcK0ms5W6q9AmDKF90C4knLQ', parse_mode='HTML')  # Установлен HTML-режим для обращения по имени

# Подключение и создание базы данных SQLite
conn = sqlite3.connect('dick_game.db', check_same_thread=False)
cursor = conn.cursor()

# Начальные данные пользователей (включая зарегистрированных)
users = [
    ('Davlet', 310, '1970-01-01 00:00:00'),
    ('Skagi', 305, '1970-01-01 00:00:00'),
    ('makbauer', 235, '1970-01-01 00:00:00'),
    ('Sosihue', 234, '1970-01-01 00:00:00'),
    ('AmiR', 218, '1970-01-01 00:00:00'),
    ('kkosttt', 175, '1970-01-01 00:00:00'),
    ('_tsakhaev_🍀', 168, '1970-01-01 00:00:00'),
    ('Banan', 122, '1970-01-01 00:00:00')
]

# Удаление таблицы users, если она уже существует
cursor.execute("DROP TABLE IF EXISTS users")

# Создание таблицы с уникальным ограничением на username
cursor.execute('''
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,  -- Уникальное ограничение для username
        length INTEGER DEFAULT 0,
        last_used TEXT DEFAULT '1970-01-01 00:00:00'
    )
''')



# Вставка или обновление данных для каждого пользователя
for user in users:
    cursor.execute("""
        INSERT INTO users (username, length, last_used)
        VALUES (?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET length=excluded.length, last_used=excluded.last_used
    """, user)
conn.commit()


# Команда для установки значений по умолчанию
def set_default_values():
    cursor.execute("UPDATE users SET length = 0 WHERE length IS NULL")
    cursor.execute("UPDATE users SET last_used = '1970-01-01 00:00:00' WHERE last_used IS NULL")
    conn.commit()

set_default_values()

# Команда /start для приветствия пользователя
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "Привет! Используй команду /dick, чтобы зарегистрироваться и начать игру.")

@bot.message_handler(commands=['dick'])
def dick_command(message):
    user_id = message.from_user.id
    username = message.from_user.first_name

    # Проверка на существование пользователя по username
    user_cursor = conn.cursor()
    user_cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    user = user_cursor.fetchone()

    # Если пользователь уже существует, обновляем его user_id и last_used
    if user:
        user_cursor.execute("UPDATE users SET user_id = ?, last_used = ? WHERE username = ?",
                            (user_id, '1970-01-01 00:00:00', username))
        conn.commit()
    else:
        # Регистрация нового пользователя
        user_cursor.execute("INSERT INTO users (user_id, username, length, last_used) VALUES (?, ?, 0, ?)",
                            (user_id, username, '1970-01-01 00:00:00'))
        conn.commit()
        bot.reply_to(message, f"<a href='tg://user?id={user_id}'>{username}</a>, ты зарегистрирован! Длина установлена на 0 см.")

    user_cursor.close()


    # Регистрация пользователя, если он не зарегистрирован
    if not user:
        register_cursor = conn.cursor()
        register_cursor.execute("INSERT INTO users (user_id, username, length, last_used) VALUES (?, ?, 0, ?)",
                                (user_id, username, '1970-01-01 00:00:00'))
        conn.commit()
        register_cursor.close()
        bot.reply_to(message, f"<a href='tg://user?id={user_id}'>{username}</a>, ты зарегистрирован! Длина установлена на 0 см.")

    # Курсор для получения обновленных данных пользователя
    user_cursor = conn.cursor()
    user_cursor.execute("SELECT length, last_used FROM users WHERE user_id=?", (user_id,))
    user = user_cursor.fetchone()
    last_used = datetime.strptime(user[1], '%Y-%m-%d %H:%M:%S')
    user_cursor.close()

    if datetime.now() - last_used >= timedelta(seconds=3):  # Установлено на 3 секунды для тестирования
        delta = random.choice(list(range(-5, 0)) + list(range(1, 11)))
        new_length = user[0] + delta

        update_cursor = conn.cursor()
        update_cursor.execute("UPDATE users SET length=?, last_used=? WHERE user_id=?",
                              (new_length, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
        conn.commit()
        update_cursor.close()

        # Определение позиции в топе
        rank_cursor = conn.cursor()
        rank_cursor.execute("SELECT user_id FROM users ORDER BY length DESC")
        rankings = [row[0] for row in rank_cursor.fetchall()]
        position = rankings.index(user_id) + 1
        rank_cursor.close()

        # Сообщение с HTML-обращением к пользователю
        if delta > 0:
            bot.reply_to(message, f"<a href='tg://user?id={user_id}'>{username}</a>, твой писюн вырос на {delta} см.\n"
                                  f"Теперь он равен {new_length} см.\n"
                                  f"Ты занимаешь {position} место в топе.\n"
                                  "Следующая попытка завтра!")
        else:
            bot.reply_to(message, f"<a href='tg://user?id={user_id}'>{username}</a>, твой писюн сократился на {-delta} см.\n"
                                  f"Теперь он равен {new_length} см.\n"
                                  f"Ты занимаешь {position} место в топе.\n"
                                  "Следующая попытка завтра!")
    else:
        # Определение текущей позиции и длины игрока
        current_length = user[0]
        rank_cursor = conn.cursor()
        rank_cursor.execute("SELECT user_id FROM users ORDER BY length DESC")
        rankings = [row[0] for row in rank_cursor.fetchall()]
        position = rankings.index(user_id) + 1
        rank_cursor.close()

        # Сообщение, если пользователь не дождался времени, с HTML-обращением
        bot.reply_to(message, f"<a href='tg://user?id={user_id}'>{username}</a>, ты уже играл.\n"
                              f"Сейчас он равен {current_length} см.\n"
                              f"Ты занимаешь {position} место в топе.\n"
                              "Следующая попытка завтра!")

# Остальные команды остаются прежними, например, /top_dick и /stats
# Запуск бота
bot.polling()
