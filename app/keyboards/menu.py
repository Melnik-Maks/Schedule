from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import BotCommand

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📆 Розклад')],
    [KeyboardButton(text='👤 Профіль')],
    [KeyboardButton(text='⚜️ Підтримка ⚜️')],
], resize_keyboard=True)

support_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Написати в підтримку", url="https://t.me/maksmyser")],
    ]
)

add_bot_to_chat = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати в групу ➕", url=f"https://t.me/ScheduleeEbot?startgroup=true")]
    ]
)


async def set_bot_commands(bot):
    commands = [
        BotCommand(command="/start", description="Запуск ⚡"),
        BotCommand(command="/group", description="Розклад у групі 🎲"),
    ]
    await bot.set_my_commands(commands)