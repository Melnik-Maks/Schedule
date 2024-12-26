from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import daysOfTheWeek

from app.database.requests import get_all_groups, get_all_subgroups_by_group

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Розклад')]], resize_keyboard=True)

async def groups():
    keyboard = InlineKeyboardBuilder()
    all_groups = await get_all_groups()
    for group in all_groups:
        keyboard.add(InlineKeyboardButton(text=group, callback_data=f"group_{group}"))
    return keyboard.adjust(1).as_markup()

async def subgroups(group: str):
    keyboard = InlineKeyboardBuilder()
    all_subgroups = await get_all_subgroups_by_group(group)
    for subgroup in all_subgroups:
        keyboard.add(InlineKeyboardButton(text=f"{group}/{subgroup}", callback_data=f"subgroup_{group}/{subgroup}"))
    return keyboard.adjust(1).as_markup()

async def days(group: str):
    keyboard = InlineKeyboardBuilder()
    for day in daysOfTheWeek:
        keyboard.add(InlineKeyboardButton(text=day, callback_data=f"day_{day}/{group}"))
    return keyboard.adjust(1).as_markup()

