from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import daysOfTheWeek

schedule = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📆 Розклад на тиждень')],
    [KeyboardButton(text='📅 Сьогодні'), KeyboardButton(text='📅 Завтра')],
    [KeyboardButton(text='📜 Оригінальний розклад')],
    [KeyboardButton(text='🏠 Додому')]
], resize_keyboard=True)

original_schedule = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📊 EXEL', url='https://docs.google.com/spreadsheets/d/1eCEO-7sEocM7HDyafVcW5bI1n1nvu7De7IxD0RFw3cE/pubhtml#')]
])

update_schedule = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🧲 Перезаписати весь розклад 🧲')],
    [KeyboardButton(text='🔁 Оновити розклад 🔁', callback_data='yes')],
    [KeyboardButton(text='🏠 Додому')]
], resize_keyboard=True)


def ask_yes_or_no() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='✅ТАК', callback_data='yes'))
    keyboard.add(InlineKeyboardButton(text='Ні❌', callback_data='no'))
    return keyboard.adjust(2).as_markup()

async def days() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for day in daysOfTheWeek:
        keyboard.add(InlineKeyboardButton(text=day, callback_data=f"day_{day}"))
    return keyboard.adjust(2).as_markup()

async def yesterday_and_tomorrow(day: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    day_number = daysOfTheWeek.index(day)
    yesterday = daysOfTheWeek[(6 + day_number - 1) % 6]
    tomorrow = daysOfTheWeek[(6 + day_number + 1) % 6]
    keyboard.add(InlineKeyboardButton(text=f"<-{yesterday}", callback_data=f"day_{yesterday}"))
    keyboard.add(InlineKeyboardButton(text=f"{tomorrow}->", callback_data=f"day_{tomorrow}"))
    return keyboard.adjust(2).as_markup()

