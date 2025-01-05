from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🔄 Змінити групу')],
    [KeyboardButton(text='🏠 Додому')]
], resize_keyboard=True)
