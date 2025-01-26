from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from config import daysOfTheWeek

from app.database.requests import is_admin

async def schedule(tg_id: int):
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(KeyboardButton(text='📆 Розклад на тиждень'))
    keyboard.row(KeyboardButton(text='📅 Сьогодні'), KeyboardButton(text='📅 Завтра'))
    keyboard.row(KeyboardButton(text='📜 Оригінальний розклад'))
    if await is_admin(tg_id):
        keyboard.row(KeyboardButton(text='🛠 Змінити розклад 🛠'))
    keyboard.row(KeyboardButton(text='🏠 Додому'))

    return keyboard.as_markup(resize_keyboard=True)


original_schedule = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📊 EXEL', url='https://docs.google.com/spreadsheets/d/1eCEO-7sEocM7HDyafVcW5bI1n1nvu7De7IxD0RFw3cE/pubhtml#')]
])

def schedule_in_exel(sheet_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='📊 Перейти в exel', url=f'https://docs.google.com/spreadsheets/d/1gdDNYOR4NW8OWTserIt0kJgSJMVURMBGJWBzbMKHc-s/edit?gid={sheet_id}#gid={sheet_id}'))
    return keyboard.adjust(1).as_markup()

def update_schedule(tg_id: int):
    keyboard = ReplyKeyboardBuilder()
    if tg_id == 722714127:
        keyboard.row(KeyboardButton(text='🧲 Перезаписати весь розклад 🧲'))
    keyboard.row(KeyboardButton(text='🖋 Редагувати розклад 🖋'))
    keyboard.row(KeyboardButton(text='🔁 Оновити розклад 🔁'))
    keyboard.row(KeyboardButton(text='🏠 Додому'))

    return keyboard.as_markup(resize_keyboard=True)


def ask_to_update_all_schedule() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='✅ТАК', callback_data='update_all_schedule_yes'))
    keyboard.add(InlineKeyboardButton(text='Ні❌', callback_data='update_all_schedule_no'))
    return keyboard.adjust(2).as_markup()

def ask_to_update_schedule_for_one_group() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='✅ТАК', callback_data='update_schedule_for_one_group_yes'))
    keyboard.add(InlineKeyboardButton(text='Ні❌', callback_data='update_schedule_for_one_group_no'))
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

