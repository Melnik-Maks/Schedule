from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.database.requests import user_has_group, get_user_reminder

profile1 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='⚙️ Налаштування')],
    [KeyboardButton(text='🏠 Додому')]
], resize_keyboard=True)

async def profile(tg_id: int, enable_reminder: bool = False):
    keyboard = ReplyKeyboardBuilder()
    if await user_has_group(tg_id):
        keyboard.row(KeyboardButton(text='🔄 Змінити групу'))
    else:
        keyboard.row(KeyboardButton(text='🔮 Обрати групу'))
    if await get_user_reminder(tg_id):
        keyboard.row(KeyboardButton(text='🔔 Вимкнути нагадування'))
    else:
        keyboard.row(KeyboardButton(text='🔕 Увімкнути нагадування'))
    keyboard.row(KeyboardButton(text='🏠 Додому'))
    return keyboard.as_markup(resize_keyboard=True)
