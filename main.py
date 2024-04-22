import os
import random
import sys
import time
import json
import logging
import subprocess
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import g4f
from aiogram.utils import executor


# Включите логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
API_TOKEN = '6754888235:AAEmBQYzwCeYEvnDy44PHKwNpThHf-hFOac'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

SPECIAL_USER_ID = 1540484392
print(g4f.Provider.Liaobots.params)
SPECIAL_USER_FILE = "special_user.json"


# Словарь для хранения истории разговоров
conversation_history = {}

# Функция для обрезки истории разговора
def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history


# @dp.message_handler(commands=['restart'])
# async def restart(message: types.Message):
#     await message.reply("Введите код подтверждения:")
#     confirmation_code = await dp.current_state(user=message.from_user.id).get('confirmation_code', default=None)
#     if confirmation_code == '3322':
#         await message.reply("Выполняется перезапуск бота. Пожалуйста, подождите!")
#         print(' / / / !RESTARTING! \ \ \ ')
#         time.sleep(0.5)
#         python = sys.executable
#         os.execl(python, python, *sys.argv)
#     else:
#         await message.reply("Код подтверждения неверен.")
    
@dp.message_handler(commands=['r331'])
async def restart(message: types.Message):
    # Generate three random activation codes
    activation_codes = [str(random.randint(1000, 9999)) for _ in range(3)]

    # Save the activation codes in the user's conversation history
    conversation_history[message.from_user.id] = activation_codes

    # Create the inline keyboard with the activation code buttons
    keyboard = InlineKeyboardMarkup()
    buttons = []
    for i, code in enumerate(activation_codes):
        button = InlineKeyboardButton(f"{code}", callback_data=code)
        buttons.append(button)
    print(buttons)
    random.shuffle(buttons)  # Shuffle the buttons
    print("/\/\/\/\/")
    print(buttons)
    print("/\/\/\/\/")
    keyboard.row(*buttons)

    # Send the confirmation code to the special user 
    await bot.send_message(SPECIAL_USER_ID, f"!!!ВЫПОЛНЯЕТСЯ ПЕРЕЗАПУСК БОТА С ВНЕШНЕГО АККАУНТА!!! \n\nКод подтверждения: {activation_codes[0]}")

    # Send the activation code buttons to the user who initiated the restart command
    await bot.send_message(message.from_user.id, "Выберите код подтверждения", reply_markup=keyboard)

    conversation_history[message.from_user.id].append(message.from_user.id)

    try:
        with open(SPECIAL_USER_FILE, "r") as f:
            special_user_ids = json.load(f)
    except FileNotFoundError:
        # If the file doesn't exist, create it with the user's ID
        with open(SPECIAL_USER_FILE, "w") as f:
            json.dump([message.from_user.id], f)
    except ValueError:
        # If the file contains a single ID instead of a list, create a new list with the user's ID
        with open(SPECIAL_USER_FILE, "w") as f:
            json.dump([message.from_user.id], f)
    else:
        # If the file exists and contains a list of IDs, append the user's ID to the list
        special_user_ids.append(message.from_user.id)
        with open(SPECIAL_USER_FILE, "w") as f:
            json.dump(special_user_ids, f)

    # with open(SPECIAL_USER_FILE, "w") as f:
    #     json.dump(message.from_user.id, f)


@dp.callback_query_handler()
async def process_callback_button(callback_query: types.CallbackQuery):
    data = callback_query.data

    # Retrieve the activation codes for the user who initiated the restart command
    user_activation_codes = conversation_history.get(callback_query.from_user.id)

    # Check if the activation code is correct
    if data in user_activation_codes:
        index = user_activation_codes.index(data)
        if index == 0:
            await bot.answer_callback_query(callback_query.id)
            await bot.send_message(callback_query.from_user.id, "Выполняется перезапуск бота. Пожалуйста, подождите!")
            # print(f"/ / /  !USER  {message.from_user.first_name} (@{message.from_user.username})REQUESTED RESTART! \ \ \ ")
            print(' / / / !RESTARTING! \ \ \ ')
            time.sleep(0.5)
            # subprocess.Popen([sys.executable, __file__])
            # sys.exit()
            # subprocess.run(["restart", "-f", "-p", str(os.getpid())])
            python = sys.executable
            os.execl(python, python, *sys.argv)
           
        else:
            # Remove the used activation code from the user's conversation history
            del user_activation_codes[index]
            conversation_history[callback_query.from_user.id] = user_activation_codes
            # await bot.answer_callback_query(callback_query.id, "Код уже использовался. Осталось: " + ', '.join(user_activation_codes), show_alert=True)
            await bot.answer_callback_query(callback_query.id, "Код неверен", show_alert=True)
    else:
        await bot.answer_callback_query(callback_query.id, "Код неверен", show_alert=True)

@dp.message_handler(commands=['ping'])
async def ping(message: types.Message):
    await message.reply("Ping!")


@dp.message_handler(commands=['start'])
async def process_clear_command(message: types.Message):

    if os.path.exists(SPECIAL_USER_FILE):
        # Load the special user ID from the file
        try:
            with open(SPECIAL_USER_FILE, "r") as f:
                special_user_ids = json.load(f)
        except FileNotFoundError:
            # If the file doesn't exist, the bot is starting for the first time
            return

        # If the file contains a single ID, use that ID
        if not isinstance(special_user_ids, list):
            special_user_ids = [special_user_ids]

        # Send a message to the special user who initiated the restart command
        if special_user_ids and special_user_ids[-1] == message.from_user.id:
            await bot.send_message(special_user_ids[-1], "Бот успешно перезапущен и готов к работе!")

        # Remove the special user ID from the file
        os.remove(SPECIAL_USER_FILE)
    else:
        #If the file doesn't exist, create it
        with open(SPECIAL_USER_FILE, "w") as f:
            json.dump([], f)
    user_id = message.from_user.id
    conversation_history[user_id] = []

    user_info = f"User: {message.from_user.first_name} (@{message.from_user.username})"  # Получить имя и тег пользователя
    with open('out.txt', 'a', encoding='utf-8') as file:
        file.write(f"{user_info} - {datetime.datetime.now()}\n")  # Запись информации о пользователе в файл
    await message.reply("Новый диалог начат, история диалога очищена.")
    print("NEW USER, PLS CHECK OUT.TXT")



# Обработчик для каждого нового сообщения
@dp.message_handler()
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_input = message.text

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    chat_history = conversation_history[user_id]



    try:
        print('\ \ \ TRYING / / /')
        await message.answer("Запрос отправлен...")
        #response = await g4f.ChatCompletion.create_async(
            #model=g4f.models.default,
            ##model=g4f.models.gpt_4,
            #messages=chat_history,
            #provider=g4f.Provider.Liaobots,
        #)
        #chat_gpt_response = response
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=chat_history,
            provider=g4f.Provider.Liaobots,
            #proxy="http://gvaeysbt:xyj2awo8lu0i@104.239.10.217:5888",
    # or socks5://user:pass@host:port
        timeout=120,  # in secs
        )
        chat_gpt_response = response
    except Exception as e:
        print(f"{g4f.Provider.Liaobots.__name__}:", e)
        chat_gpt_response = "Извините, произошла ошибка." ,e
    # await message.delete()

    conversation_history[user_id].append({"role": "assistant", "content": chat_gpt_response})
    print(conversation_history)
    length = sum(len(message["content"]) for message in conversation_history[user_id])
    print(length)
    await message.answer(chat_gpt_response)


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


