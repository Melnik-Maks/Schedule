from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import daysOfTheWeek

from app.database.requests import get_all_specialties, get_all_groups_by_specialty, get_all_subgroups_by_group


schedule = ReplyKeyboardMarkup(keyboard=
    [[KeyboardButton(text='Розклад')],
    [KeyboardButton(text='Розклад на сьогодні')],
    [KeyboardButton(text='Змінити групу')]],
                               resize_keyboard=True)


'''schedule = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Розклад', callback_data='schedule')],
    [InlineKeyboardButton(text='Змінити групу', callback_data='reset_group')]
])'''

async def specialties():
    keyboard = InlineKeyboardBuilder()
    all_specialties = await get_all_specialties()
    for specialty in all_specialties:
        keyboard.add(InlineKeyboardButton(text=specialty, callback_data=f"specialty_{specialty}"))
    return keyboard.adjust(1).as_markup()

async def groups(specialty: str):
    keyboard = InlineKeyboardBuilder()
    all_groups = await get_all_groups_by_specialty(specialty)
    for group in all_groups:
        keyboard.add(InlineKeyboardButton(text=f"{specialty}-{group}", callback_data=f"group_{specialty}-{group}"))
    keyboard.add(InlineKeyboardButton(text=f"<-", callback_data=f"goback_specialty"))
    return keyboard.adjust(1).as_markup()

async def subgroups(specialty_group: str):
    keyboard = InlineKeyboardBuilder()
    all_subgroups = await get_all_subgroups_by_group(specialty_group.split('-')[1])
    for subgroup in all_subgroups:
        keyboard.add(InlineKeyboardButton(text=f"{specialty_group}/{subgroup}", callback_data=f"subgroup_{specialty_group}/{subgroup}"))
    keyboard.add(InlineKeyboardButton(text=f"<-", callback_data=f"goback_group_{specialty_group.split('-')[0]}"))
    return keyboard.adjust(1).as_markup()

async def days():
    keyboard = InlineKeyboardBuilder()
    for day in daysOfTheWeek:
        keyboard.add(InlineKeyboardButton(text=day, callback_data=f"day_{day}"))
    return keyboard.adjust(2).as_markup()

