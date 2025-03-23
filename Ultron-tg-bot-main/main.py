import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

# Конфигурация бота
TOKEN = "СЮДА ТОКЕН БОТА"
ADMIN_ID = [СЮДА ИД ТГ АДМИНА]

# Создание экземпляров бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
questions = {}

# Функция для получения ID пользователя
def ch_id(message: types.Message) -> int:
    return message.from_user.id

# Обработчик команды /start
@dp.message(F.text == "/start")
async def welcome(message: types.Message):
    first_name = message.from_user.first_name or "Пользователь"
    await message.answer(f"Привет, {first_name}! Отправка фото, стикеров, видео, всё кроме текста не работает. Удачи!")

# Функция уведомления администраторов о новом вопросе
async def notify_admins(message: types.Message, author: str):
    for admin_id in ADMIN_ID:
        await bot.send_message(admin_id, f"Доступен новый вопрос от @{author}")

# Обработчик команды /list_questions
@dp.message(F.text == "/list_questions")
async def list_questions(message: types.Message):
    if message.from_user.id in ADMIN_ID:
        if not questions:
            await message.answer("Нет доступных вопросов.")
            return
        content = "\n".join([f"ID: {k}\nInfo: {v['Info']}\nВопрос: {v['question']}\n" for k, v in questions.items()])
        await message.answer(content)

# Обработчик команды /help
@dp.message(F.text == "/help")
async def help_command(message: types.Message):
    await message.answer("Отправьте свой вопрос, и он будет отправлен администратору.")

# Обработчик команды /id
@dp.message(F.text == "/id")
async def get_id(message: types.Message):
    await message.answer(f"Ваш ID: {ch_id(message)}")

# Обработчик команды /answer
@dp.message(F.text == "/answer")
async def answer_question(message: types.Message):
    if message.from_user.id not in ADMIN_ID:
        await message.answer("Вы не являетесь администратором.")
        return
    if not questions:
        await message.answer("Список вопросов пуст.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=value['question'], callback_data=str(key))]
        for key, value in questions.items()
    ])
    await message.answer("Выберите вопрос, на который хотите ответить:", reply_markup=keyboard)

# Обработчик выбора вопроса администратором
@dp.callback_query(F.data.func(lambda data: data.isdigit()))
async def callback_query(call: types.CallbackQuery):
    if call.from_user.id in ADMIN_ID:
        question_id = int(call.data)
        if question_id in questions:
            await bot.send_message(call.message.chat.id, f"Выбранный вопрос: {questions[question_id]['question']}")
            await bot.send_message(call.message.chat.id, "Введите ответ на вопрос:")
        else:
            await bot.send_message(call.message.chat.id, "Вопрос не найден.")
    else:
        await bot.send_message(call.message.chat.id, "Вы не являетесь администратором.")

# Обработчик текстовых сообщений пользователей
@dp.message()
async def handle_text_message(message: types.Message):
    first_name = message.from_user.first_name or "Неизвестный"
    username = message.from_user.username or "Без username"
    chat_id = ch_id(message)
    text = message.text.strip()
    questions[chat_id] = {"Info": first_name, "id": chat_id, "question": text}
    await message.answer("Ваш вопрос отправлен, скоро на него ответит наш админ")
    await notify_admins(message, username)

# Основная функция запуска бота
async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())