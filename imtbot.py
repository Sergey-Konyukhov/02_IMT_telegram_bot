import telebot
import config
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

# Хранилище данных пользователей для расчёта
user_data = {}

@bot.message_handler(commands=['start'])
def welcome_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Новый расчёт")
    markup.add(item1)

    bot.send_message(message.chat.id, "Добро пожаловать, {message.from_user.first_name}! Этот бот умеет рассчитывать Индекс массы тела (ИМТ).\nДля начала нажмите на кнопку: 'Новый расчёт'",
                     parse_mode='html', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id

    if message.chat.type == 'private':
        if message.text == 'Новый расчёт':
            bot.send_message(chat_id, "Во-первых, укажите рост в метрах.\nНапример: 1.65 или 2.1")
            user_data[chat_id] = {'step': 'height'}

        elif chat_id in user_data and user_data[chat_id].get('step') == 'height':
            try:
                height = float(message.text.replace(',', '.'))
                if height <= 0:
                    raise ValueError("Height must be positive")
                user_data[chat_id]['height'] = height
                user_data[chat_id]['step'] = 'weight'
                bot.send_message(chat_id, "Во-вторых, укажите вес в килограммах.\nНапример: 70 или 85.5")
            except ValueError:
                bot.send_message(chat_id, "Пожалуйста, введите значение роста в корректном формате, например: 1.65")

        elif chat_id in user_data and user_data[chat_id].get('step') == 'weight':
            try:
                weight = float(message.text.replace(',', '.'))
                if weight <= 0:
                    raise ValueError("Weight must be positive")
                user_data[chat_id]['weight'] = weight

                # Расчет ИМТ
                height = user_data[chat_id]['height']
                bmi = weight / (height ** 2)

                # Категория ИМТ
                if bmi < 18.5:
                    category = "недостаточный вес"
                elif 18.5 <= bmi < 24.9:
                    category = "нормальный вес"
                elif 25 <= bmi < 29.9:
                    category = "избыточный вес"
                else:
                    category = "ожирение"

                bot.send_message(chat_id, f"Ваш ИМТ: {bmi:.2f}. Это {category}.")

                # Очистка данных пользователя
                user_data.pop(chat_id, None)

            except ValueError:
                bot.send_message(chat_id, "Пожалуйста, введите значение веса в корректном формате, например: 70")

        else:
            bot.send_message(chat_id, 'Нажмите "Новый расчёт", чтобы начать заново.')

# Запуск бота
bot.polling(none_stop=True)