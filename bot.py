import requests
import json
import time
# Импортируйте библиотеку для кодирования в Base64
import requests
from io import BytesIO
from PIL import Image
import pytesseract 
import cv2
import pickle
import numpy as np

import base64
from datetime import datetime
from telegram import (Update, File)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

import database
add_class=False
classed=''
understend_criteria=False
criteria=''
role='Teacher' #Student
choose_text='Handwritten' #printed
telegram_token = ""
yandex_cloud_catalog = ""
yandex_gpt_api_key = ""
yandex_gpt_model = "yandexgpt"

database = database.Database("database.db")


async def file_to_numpy(file: File):
    image_bytes = BytesIO(await file.download_as_bytearray())  # Download the file content as a bytearray

    # Load the image using PIL (Pillow)
    image = Image.open(image_bytes)
    
    # Convert the image to a numpy array
    image_array = np.array(image)
    
    return image_array


async def file_to_b64(file: File):
    image_bytes = BytesIO(await file.download_as_bytearray())  # Download the file content as a bytearray

    # Load the image using PIL (Pillow)
    image = Image.open(image_bytes)
    
    # Convert the image to a numpy array
    image_array = base64.b64encode(image)
    
    return image_array



async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
            global criteria
            global understend_criteria
            global add_class
            global classed
            image_file = await update.message.photo[-1].get_file()  # Получение файла из сообщения
            try:
                await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Запрос получен, ожидайте свою очередь")
                if image_file is not None:
                    #print(333, image_file,type(image_file))
                    if choose_text.lower() == 'printed':
                        print(11111)
                        text = pytesseract.image_to_string(await file_to_numpy(image_file), lang='rus')
                    else:
                        print(2222)
                        custom_config = r'--oem 1 --psm 6 lstmbox'
                        text = pytesseract.image_to_string(cv2.cvtColor(await file_to_numpy(image_file), cv2.COLOR_RGB2GRAY), config=custom_config,lang='rus')
                        #text = send_ocr_request(photo=file_to_b64(image_file),update=update,context=context)

                if not understend_criteria and not add_class:

                    print(text)
                    if len(criteria)>0:
                        system_prompt = (
                                            f"Ты профессиональный учитель, проверь правильность выполненной работы по следующим критериям: {criteria} и напиши, где ошибки"
                                        )
                    else:
                        system_prompt = (
                                            "Ты профессиональный учитель, проверь правильность выполненной работы и напиши где ошибки: "
                                        )
                    print(1)
                    await send_gpt_request(system_prompt=system_prompt,user_prompt=text, context=context,update=update)
                    print(2)
                elif understend_criteria and not add_class:
                     criteria=text
                     await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Критерии проверки работ сохранены")
                     understend_criteria = False
                elif not understend_criteria and add_class:
                     classed = classed[update.effective_chat.id].append(text)
                     with open('class.pkl', 'wb') as f:
                        pickle.dump(classed, f)
                     await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Новый обучающийся добавлен в класс")
                     add_class = False
            except:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text='Введите читаемый запрос',
                )






async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Я Эдьюс, умный помошник для проверки контрольных работ. Отправь мне картинку с проверочной работой или текст этой контрольной",
    )

async def get_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Функция проходит стадию доработки. Приносим извенения за доставленные неудобства")
async def take_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #print(1,choose_text)
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Функция проходит стадию доработки. Приносим извенения за доставленные неудобства")

async def get_criteria(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global understend_criteria
        understend_criteria=True
        #print(1,choose_text)
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Введите критерии проверки работы")

async def del_criteria(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global criteria 
        criteria = ''
        #print(1,choose_text)
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Критерии проверки работ удалены")
async def show_criteria(update: Update, context: ContextTypes.DEFAULT_TYPE):
        #print(1,choose_text)
        if len(criteria)>0:
            await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Текущие критерии проверки работ: {criteria}")
        else:
             await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Критерии не заданы")

async def choose_role_teacher(update: Update, context: ContextTypes.DEFAULT_TYPE):
        role="Teacher"
        print(1,choose_text)
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Текущий пользователь: {role}")

async def choose_role_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
        role="Student"
        print(1,choose_text)
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Текущий пользователь: {role}")


async def choose_handlewritten(update: Update, context: ContextTypes.DEFAULT_TYPE):
        choose_text="Handlewritten"
        print(1,choose_text)
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Тип читаемого текста с изображения: {choose_text}")


async def choose_printed(update: Update, context: ContextTypes.DEFAULT_TYPE):
        choose_text="Printed"
        print(2,choose_text)
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Тип читаемого текста с изображения: {choose_text}")

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global understend_criteria
    global criteria
    global add_class
    global classed
    text_len = len(update.message.text)
    database.add_counter(update.effective_chat.id, text_len)
    
    if not understend_criteria and not add_class:
        if len(criteria)>0:
            system_prompt = (
                                f"Ты профессиональный учитель, проверь правильность выполненной работы по следующим критериям: {criteria} и напиши, где ошибки"
                            )
        else:
            system_prompt = (
                                "Ты профессиональный учитель, проверь правильность выполненной работы и напиши где ошибки: "
                            )
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Запрос получен, ожидайте свою очередь")
    
        answer = await send_gpt_request(system_prompt=system_prompt, user_prompt=update.message.text, context=context,update=update)
        if answer:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)

        elif understend_criteria and not add_class:
                     criteria=text
                     await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Критерии проверки работ сохранены")
                     understend_criteria = False
                


    elif understend_criteria and not add_class:
         criteria = update.message.text
         await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Критерии проверки работ сохранены")
         understend_criteria = False
         #print(understend_criteria)
    elif not understend_criteria and add_class:
                     classed = classed[update.effective_chat.id].append(update.message.text)
                     with open('class.pkl', 'wb') as f:
                        pickle.dump(classed, f)
                     await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Новый обучающийся добавлен в класс")
                     add_class = False
         
   

async def send_gpt_request(system_prompt: str, user_prompt: str,context: ContextTypes.DEFAULT_TYPE,update: Update):
    body = {
        "modelUri": f"gpt://{yandex_cloud_catalog}/{yandex_gpt_model}",
        "completionOptions": {"stream": False, "temperature": 0.4, "maxTokens": "20000"},
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": user_prompt},
        ],
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {yandex_gpt_api_key}",
        "x-folder-id": yandex_cloud_catalog,
    }
    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        return "ERROR"

    
    response_json = json.loads(response.text)
    operation_id = response_json["id"]

    url = f"https://llm.api.cloud.yandex.net/operations/{operation_id}"
    headers = {"Authorization": f"Api-Key {yandex_gpt_api_key}"}

    while True:
        response = requests.get(url, headers=headers)
        response_json = json.loads(response.text)
        done = response_json["done"]
        if done:
            break
        else:
            time.sleep(0.5)

    answer = response_json["response"]["alternatives"][0]["message"]["text"]
    if len(answer) == 0:
        return "ERROR"
    
    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Благодарим Вас за ожидание.")
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer,
    )
    print(answer)

    

"""
    temperature = 0.4
    seed = int(round(datetime.now().timestamp()))
    body = {
    "modelUri": f"art://{yandex_cloud_catalog}/yandex-art/latest",
    "generationOptions": {"seed": seed, "temperature": temperature},
    "messages": [
        {"weight": 1, "text": answer},
    ],
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"
    headers = {"Authorization": f"Api-Key {yandex_gpt_api_key}"}

    response = requests.post(url, headers=headers, json=body)
    response_json = json.loads(response.text)
    print(response_json)
    operation_id = response_json["id"]

    url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
    headers = {"Authorization": f"Api-Key {yandex_gpt_api_key}"}

    while True:
        response = requests.get(url, headers=headers)
        response_json = json.loads(response.text)
        done = response_json["done"]
        if done:
            break
        else:
            time.sleep(2)
    print(222222)

    image_data = response_json["response"]["image"]
    
    return base64.b64decode(image_data)"""


if __name__ == "__main__":
    start_handler = CommandHandler("start", start)
    chooser_handlewritten_handler = CommandHandler("choose_handlewritten", choose_handlewritten)
    chooser_printed_handler = CommandHandler("choose_printed", choose_printed)
    chooser_role_teacher = CommandHandler("choose_teacher", choose_role_teacher)
    chooser_role_student = CommandHandler("choose_student", choose_role_student)
    understanding_criteria = CommandHandler("understand_criteria", get_criteria)
    delete_criteria = CommandHandler("del_criteria", del_criteria)
    showing_criteria = CommandHandler("show_criteria", show_criteria)
    getting_class = CommandHandler("get_class", get_class)
    taking_class = CommandHandler("take_class", take_class)
    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), text)
    image_handler = MessageHandler(filters.PHOTO, image)

    application = ApplicationBuilder().token(telegram_token).build()
    application.add_handler(image_handler)
    application.add_handler(start_handler)
    application.add_handler(chooser_printed_handler)
    application.add_handler(chooser_handlewritten_handler)
    application.add_handler(chooser_role_teacher)
    application.add_handler(chooser_role_student)
    application.add_handler(understanding_criteria)
    application.add_handler(delete_criteria)
    application.add_handler(showing_criteria)
    application.add_handler(getting_class)
    application.add_handler(taking_class)
    application.add_handler(text_handler)
    application.run_polling()
