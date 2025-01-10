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


async def days():
    keyboard = InlineKeyboardBuilder()
    for day in daysOfTheWeek:
        keyboard.add(InlineKeyboardButton(text=day, callback_data=f"day_{day}"))
    return keyboard.adjust(2).as_markup()

async def yesterday_and_tomorrow(day: str):
    keyboard = InlineKeyboardBuilder()
    day_number = daysOfTheWeek.index(day)
    yesterday = daysOfTheWeek[(6 + day_number - 1) % 6]
    tomorrow = daysOfTheWeek[(6 + day_number + 1) % 6]
    keyboard.add(InlineKeyboardButton(text=f"<-{yesterday}", callback_data=f"day_{yesterday}"))
    keyboard.add(InlineKeyboardButton(text=f"{tomorrow}->", callback_data=f"day_{tomorrow}"))
    return keyboard.adjust(2).as_markup()
