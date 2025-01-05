from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📅 Розклад')],
    [KeyboardButton(text='👤 Профіль')],
    [KeyboardButton(text='⚜️ Підтримка ⚜️')],
], resize_keyboard=True)

support_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Написати в підтримку", url="https://t.me/maksmyser")],
    ]
)

