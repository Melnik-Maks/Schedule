from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='⚙️ Налаштування')],
    [KeyboardButton(text='🏠 Додому')]
], resize_keyboard=True)

settings_with_enable_reminders = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🔄 Змінити групу')],
    [KeyboardButton(text='🔔 Вимкнути нагадування')],
    [KeyboardButton(text='🏠 Додому')]
], resize_keyboard=True)

settings_with_disable_reminders = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🔄 Змінити групу')],
    [KeyboardButton(text='🔕 Увімкнути нагадування')],
    [KeyboardButton(text='🏠 Додому')]
], resize_keyboard=True)