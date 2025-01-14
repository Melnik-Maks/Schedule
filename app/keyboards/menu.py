from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import BotCommand

async def menu(tg_id: int):
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(KeyboardButton(text='📆 Розклад'))
    keyboard.row(KeyboardButton(text='👤 Профіль'))
    if tg_id == 722714127:
        keyboard.row(KeyboardButton(text='🛠 Оновити розклад 🛠'))
    keyboard.row(KeyboardButton(text='⚜️ Підтримка ⚜️'))
    return keyboard.as_markup(resize_keyboard=True)

def profile(enable_reminder: bool = False):
    keyboard = ReplyKeyboardBuilder([])
    keyboard.row(KeyboardButton(text='🔄 Змінити групу'))
    if enable_reminder:
        keyboard.row(KeyboardButton(text='🔔 Вимкнути нагадування'))
    else:
        keyboard.row(KeyboardButton(text='🔕 Увімкнути нагадування'))
    keyboard.row(KeyboardButton(text='🏠 Додому'))




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