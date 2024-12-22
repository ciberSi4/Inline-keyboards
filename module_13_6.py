# Домашнее задание по теме "Инлайн клавиатуры".
# ВНИМАНИЕ: Данный код разработан в учебных целях, комментарии добавлены для себя!!!

from aiogram import Bot, Dispatcher, types  # Импортируем основные классы и типы из библиотеки aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Импорт класса для хранения состояния пользователя в памяти
from aiogram.dispatcher import FSMContext  # Контекст для работы с машиной состояний
from aiogram.dispatcher.filters.state import State, StatesGroup  # Класс для создания состояний и групп состояний
from aiogram.types import (
    ReplyKeyboardMarkup,  # Класс для создания обычной клавиатуры
    KeyboardButton,  # Класс для создания кнопки на обычной клавиатуре
    InlineKeyboardButton,  # Класс для создания кнопки на инлайн-клавиатуре
    InlineKeyboardMarkup,  # Класс для создания инлайн-клавиатуры
)
from aiogram.utils import executor  # Утилита для запуска бота

api = ""  # Токен бота

bot = Bot(token = api)  # Инициализация объекта бота
dp = Dispatcher(bot, storage = MemoryStorage())  # Инициализация диспетчера с хранилищем состояний в памяти

# Обычная клавиатура
keyboard = ReplyKeyboardMarkup(resize_keyboard = True)  # Создаем объект обычной клавиатуры с возможностью подгонки размера
buttons = [KeyboardButton('Рассчитать'), KeyboardButton('Информация')]  # Список кнопок для добавления на обычную клавиатуру
keyboard.add(*buttons)  # Добавление кнопок на клавиатуру

# Инлайн-клавиатура
inline_kb = InlineKeyboardMarkup(row_width = 2)  # Создаем объект инлайн-клавиатуры с шириной строки в 2 кнопки
btn_calculate = InlineKeyboardButton(  # Создаем кнопку для расчета калорий
    text = "Рассчитать норму калорий",
    callback_data = "calories"  # Уникальный идентификатор для этой кнопки
)
btn_formula = InlineKeyboardButton(  # Создаем кнопку для отображения формулы
    text = "Формулы расчёта",
    callback_data = "formulas"  # Уникальный идентификатор для этой кнопки
)
inline_kb.add(btn_calculate, btn_formula)  # Добавляем обе кнопки на инлайн-клавиатуру

# Машина состояний
class UserState(StatesGroup):  # Создаем класс для определения состояний
    age = State()  # Состояние для ввода возраста
    growth = State()  # Состояние для ввода роста
    weight = State()  # Состояние для ввода веса

# Команда /start
@dp.message_handler(commands = ["start"])  # Декоратор для обработки команды /start
async def start_message(message: types.Message):  # Функция-обработчик команды /start
    await message.answer("Привет! Я бот, помогающий твоему здоровью.", reply_markup = keyboard)  # Отправляем приветственное сообщение с обычной клавиатурой

# Кнопка 'Рассчитать'
@dp.message_handler(lambda message: message.text == 'Рассчитать')  # Декоратор для обработки сообщения с текстом 'Рассчитать'
async def main_menu(message: types.Message):  # Функция-обработчик нажатия на кнопку 'Рассчитать'
    await message.answer("Выберите опцию:", reply_markup = inline_kb)  # Отправляем сообщение с инлайн-клавиатурой

# Обработчик для кнопки 'Формулы расчёта'
@dp.callback_query_handler(lambda call: call.data == "formulas")  # Декоратор для обработки нажатия на кнопку с callback_data = "formulas"
async def get_formulas(call: types.CallbackQuery):  # Функция-обработчик нажатия на кнопку 'Формулы расчёта'
    formula_text = "10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (г) - 161"  # Текст формулы
    await call.message.answer(formula_text)  # Отправляем формулу пользователю

# Начало ввода возраста после нажатия на кнопку 'Рассчитать норму калорий'
@dp.callback_query_handler(lambda call: call.data == "calories")  # Декоратор для обработки нажатия на кнопку с callback_data = "calories"
async def set_age(call: types.CallbackQuery, state: FSMContext):  # Функция-обработчик нажатия на кнопку 'Рассчитать норму калорий'
    await call.message.answer('Введите свой возраст:')  # Запрашиваем у пользователя возраст
    await UserState.age.set()  # Устанавливаем состояние для ввода возраста

# Ввод роста
@dp.message_handler(state = UserState.age)  # Декоратор для обработки сообщений в состоянии ввода возраста
async def set_growth(message: types.Message, state: FSMContext):  # Функция-обработчик ввода роста
    await state.update_data(age = int(message.text))  # Сохраняем введенный возраст в контексте состояния
    await message.answer('Введите свой рост:')  # Запрашиваем у пользователя рост
    await UserState.next()  # Переходим к следующему состоянию (ввод роста)

# Ввод веса
@dp.message_handler(state = UserState.growth)  # Декоратор для обработки сообщений в состоянии ввода роста
async def set_weight(message: types.Message, state: FSMContext):  # Функция-обработчик ввода веса
    await state.update_data(growth = float(message.text))  # Сохраняем введенный рост в контексте состояния
    await message.answer('Введите свой вес:')  # Запрашиваем у пользователя вес
    await UserState.next()  # Переходим к следующему состоянию (ввод веса)

# Расчет нормы калорий
@dp.message_handler(state = UserState.weight)  # Декоратор для обработки сообщений в состоянии ввода веса
async def send_calories(message: types.Message, state: FSMContext):  # Функция-обработчик расчета нормы калорий
    await state.update_data(weight = float(message.text))  # Сохраняем введенный вес в контексте состояния

    user_data = await state.get_data()  # Получаем все сохраненные данные из контекста состояния
    age = user_data['age']  # Извлекаем возраст
    growth = user_data['growth']  # Извлекаем рост
    weight = user_data['weight']  # Извлекаем вес

    calories_norm = 10 * weight + 6.25 * growth - 5 * age + 5  # Рассчитываем норму калорий

    await message.answer(f"Ваша норма калорий: {calories_norm:.2f}")  # Сообщаем пользователю результат
    await state.finish()  # Завершаем работу с состоянием

# Обработчик всех остальных сообщений
@dp.message_handler()  # Декоратор для обработки любых других сообщений
async def all_message(message: types.Message):  # Функция-обработчик всех прочих сообщений
    await message.answer("Введите команду /start, чтобы начать общение.")  # Просим пользователя ввести команду /start

if __name__ == "__main__":  # Проверка, что скрипт запущен напрямую, а не импортирован
    executor.start_polling(dp, skip_updates = True)  # Запускаем бесконечный цикл опроса сервера Telegram на наличие новых сообщений