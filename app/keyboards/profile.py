from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

profile1 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='⚙️ Налаштування')],
    [KeyboardButton(text='🏠 Додому')]
], resize_keyboard=True)

def profile(enable_reminder: bool = False):
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(KeyboardButton(text='🔄 Змінити групу'))
    if enable_reminder:
        keyboard.row(KeyboardButton(text='🔔 Вимкнути нагадування'))
    else:
        keyboard.row(KeyboardButton(text='🔕 Увімкнути нагадування'))
    keyboard.row(KeyboardButton(text='🏠 Додому'))
    return keyboard.as_markup(resize_keyboard=True)
