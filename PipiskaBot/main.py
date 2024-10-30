import telebot
from config import token
bot = telebot.TeleBot(token)
'''print('Hello')'''
@bot.message_handler(commands=['start'])
def start(message):
        bot.send_message(message.chat.id, '''Привет! я линейка — бот для <b>чатов (групп)</b>
        
Смысл бота: бот работает только в чатах.Раз в 24 часа игрок может прописать команду /dick, где в ответ получит от бота рандомное число.
Рандом работает от -5 см до +10 см.''', parse_mode = "html")

@bot.message_handler(commands=['dick'])
def dick(message):
    bot.send_message(message.chat.id, "Пиписька выросла")

@bot.message_handler(commands=['top_dick'])
def top_dick(message):
    bot.send_message(message.chat.id, "Топ писек")

@bot.message_handler(commands=['stats'])
def stats(message):
    bot.send_message(message.chat.id, "Картинка статы писек")

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