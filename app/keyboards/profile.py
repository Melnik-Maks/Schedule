from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='⚙️ Налаштування')],
    [KeyboardButton(text='🏠 Додому')]
], resize_keyboard=True)

settings = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🔄 Змінити групу')],
    [KeyboardButton(text='⚙️ Нагадування про пари')],
    [KeyboardButton(text='👤 Профіль')]
], resize_keyboard=True)