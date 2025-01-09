from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_all_specialties, get_all_courses,get_all_groups, get_all_subgroups

async def specialties(add_button_go_back: bool = True, is_chat: bool = False):
    keyboard = InlineKeyboardBuilder()
    all_specialties = await get_all_specialties()
    for specialty in all_specialties:
        keyboard.add(InlineKeyboardButton(text=specialty, callback_data=f"course_{specialty}"))
    if add_button_go_back and not is_chat:
        keyboard.add(InlineKeyboardButton(text=f"<-", callback_data=f"settings"))
    elif add_button_go_back:
        keyboard.add(InlineKeyboardButton(text=f"<-", callback_data=f"go_back_to_chat"))
    return keyboard.adjust(1).as_markup()

async def courses(specialty: str):
    keyboard = InlineKeyboardBuilder()
    all_courses = await get_all_courses(specialty)
    for course in all_courses:
        keyboard.add(InlineKeyboardButton(text=f"{course} курс", callback_data=f"group_{specialty}_{course}"))
    keyboard.add(InlineKeyboardButton(text=f"<-", callback_data=f"specialty"))
    return keyboard.adjust(1).as_markup()

async def groups(specialty: str, course: str):
    keyboard = InlineKeyboardBuilder()
    all_groups = await get_all_groups(specialty, course)
    for group in all_groups:
        keyboard.add(InlineKeyboardButton(text=f"{specialty}-{course}{group}", callback_data=f"subgroup_{specialty}_{course}_{group}"))
    keyboard.add(InlineKeyboardButton(text=f"<-", callback_data=f"course_{specialty}"))
    return keyboard.adjust(1).as_markup()

async def subgroups(specialty: str, course: str, group: str):
    keyboard = InlineKeyboardBuilder()
    all_subgroups = await get_all_subgroups(specialty, course, group)
    for subgroup in all_subgroups:
        keyboard.add(InlineKeyboardButton(text=f"{specialty}-{course}{group}/{subgroup}", callback_data=f"setGroup_{specialty}-{course}{group}/{subgroup}"))
    keyboard.add(InlineKeyboardButton(text=f"<-", callback_data=f"group_{specialty}_{course}"))
    return keyboard.adjust(1).as_markup()
