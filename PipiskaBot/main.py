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
@bot.message_handler(commands=['start'])
def start(message):
        bot.send_message(message.chat.id, '''Привет! я линейка — бот для <b>чатов (групп)</b>
        
Смысл бота: бот работает только в чатах.Раз в 24 часа игрок может прописать команду /dick, где в ответ получит от бота рандомное число.
Рандом работает от -5 см до +10 см.''', parse_mode = "html")

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

@bot.message_handler(commands=['top_dick'])
def top_dick_command(message):
    cursor.execute("SELECT username, length FROM users ORDER BY length DESC LIMIT 10")
    top_users = cursor.fetchall()
    if top_users:
        top_message = "Топ игроков\n" + "\n".join([f"{i + 1}| {user[0]} — {user[1]} см"
                                                      for i, user in enumerate(top_users)])
        bot.reply_to(message, top_message)
    else:
        bot.reply_to(message, "Пока нет данных для отображения топа.")


# Установка бэкэнда для matplotlib
plt.switch_backend('Agg')

@bot.message_handler(commands=['stats'])
def stats_command(message):
    cursor.execute("SELECT username, length FROM users ORDER BY length DESC LIMIT 10")
    top_users = cursor.fetchall()

    if top_users:
        players = [user[0] for user in top_users]
        sizes = [max(user[1], 0) for user in top_users]  # Заменяем отрицательные значения на 0
        colors = ['#636efb', '#ef553b', '#00cd95', '#ac63fa', '#ffa15b', '#18d3f2', '#ff6692', '#b5e87f'] * (
                    len(players) // 8 + 1)

        # Сортировка данных по убыванию
        sorted_data = sorted(zip(sizes, players, colors), reverse=True)
        sizes, players, colors = zip(*sorted_data)

        # Определение сектора для "выпирания" (лидера)
        explode = [0.05 if size == max(sizes) else 0 for size in sizes]

        # Создание круговой диаграммы
        fig, ax = plt.subplots(figsize=(7, 5))
        wedges, texts, autotexts = ax.pie(sizes, autopct='%1.1f%%', startangle=25.5, colors=colors, explode=explode,
                                          radius=0.8)

        for autotext, size in zip(autotexts, sizes):
            if size == max(sizes):
                autotext.set_color('white')

        centre_circle = plt.Circle((0, 0), 0.2, fc='white')
        fig.gca().add_artist(centre_circle)

        ax.set_position([-0.0005, 0.1, 0.6, 0.8])
        plt.title('MB Fam❤️ by @pipisabot', loc='left', pad=20)

        legend_labels = [f"{size}см. - {player}" for size, player in zip(sizes, players)]
        plt.legend(legend_labels, loc="center left", bbox_to_anchor=(1, 0.5), frameon=False,
                   handlelength=1.3, handleheight=1.5)

        # Сохранение диаграммы в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)


        # Отправка диаграммы в чат
        bot.send_photo(message.chat.id, buf)
    else:
        bot.reply_to(message, "Нет данных для создания диаграммы.")

@bot.message_handler(commands=['global_top'])
def global_top(message):
    bot.send_message(message.chat.id, "Глобальный топ")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, '''<b>Команды бота:</b>
/dick — Вырастить/уменьшить пипису
/top_dick — Топ 10 пипис чата
/stats — Статистика в виде картинки
/global_top — Глобальный топ 10 игроков
/buy — Покупка доп. попыток

<b>Контакты:</b>
Наш канал — @pipisa_news
Наш чат — https://t.me/+Vc5u7PMtm543YWVi''', parse_mode = "html", disable_web_page_preview=True)

@bot.message_handler(commands=['buy'])
def buy(message):
    bot.send_message(message.chat.id, "Купить попытки")


bot.polling(none_stop=True, interval=0)