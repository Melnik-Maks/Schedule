from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import daysOfTheWeek


main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Розклад')]], resize_keyboard=True)

async def days():
    keyboard = InlineKeyboardBuilder()
    for day in daysOfTheWeek:
        keyboard.add(InlineKeyboardButton(text=day, callback_data=f"day_{day}"))
    return keyboard.adjust(1).as_markup()

