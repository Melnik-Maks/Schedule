from gc import callbacks
import asyncio

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.markdown import bold, italic, code
from aiogram.fsm.context import FSMContext
from pyasn1_modules.rfc8018 import algid_hmacWithSHA1
from sqlalchemy.util import await_fallback
import random



import app.keyboards as kb
import app.database.requests as rq
import config
from app.utils import send_schedule


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.chat.type == "private":
        await rq.set_user(message.from_user.id)
        await message.answer_sticker("CAACAgIAAxUAAWd60zJewJz6pJWWiOPKTYVTpt_vAALNYgACfJOZSrLb9emXVeS9NgQ")
        await message.answer('<b>Привіт! 👋</b>\nЯ бот, який допоможе тобі зручно переглядати розклад 📅!', parse_mode='HTML', reply_markup=await kb.menu(message.from_user.id))

    elif message.chat.type in ["group", "supergroup"]:
        await message.answer_sticker("CAACAgIAAxUAAWd60zJewJz6pJWWiOPKTYVTpt_vAALNYgACfJOZSrLb9emXVeS9NgQ")
        await message.answer('<b>Привіт! 👋</b>\n<i>Я бот, який надсилатиме нагадування про лекції 🛎️!</i>\n'
                             '<b>📍Спершу потрібно обрати групу, для якої надсилати нагадування.</b>\n🔹 <i>Просто введи команду</i> /group, <i>щоб вибрати або змінити групу!</i>', parse_mode='HTML')


@router.message(Command('group'))
async def group(message: Message):
    if message.chat.type == "private":
        await message.answer(
            "<b>Для того, щоб отримувати актуальний розклад, у вашій групі:</b>\n"
            "1. Додайте <a href='https://t.me/ScheduleeEbot'>@ScheduleeEbot</a> в спільний чат\n"
            "2. Потрібно видати права на повідомлення:\n"
            "<i>(Налаштування чату → Адміністратори → Додати адміністратора → ScheduleeEbot)</i>\n"
            "3. Прописуємо в чаті <code>/group</code>, вибираємо курс, спеціальність",
            parse_mode="HTML",
            reply_markup=kb.add_bot_to_chat,
        )
    elif message.chat.type in ["group", "supergroup"]:
        chat = await rq.get_chat_by_chat_id(message.chat.id)
        if chat:
            await message.answer(f'🎓 <b>Оберіть спеціальність:</b>', parse_mode='HTML', reply_markup=await kb.specialties(add_button_go_back=True, is_chat=True))
        else:
            await message.answer('🎓 <b>Оберіть спеціальність:</b>', reply_markup=await kb.specialties(False), parse_mode='HTML')

@router.message(Command('add'))
async def add_admin(message: Message):
    from main import bot
    user_id_str = message.text[4:].strip()
    if user_id_str.isdigit():
        user_id = int(user_id_str)
        user_exist = await rq.get_user_by_user_id(user_id)
        if user_exist:
            user = await bot.get_chat(user_id_str)
            if not user_exist.is_admin:
                await rq.add_admin(user_id)
                user = await bot.get_chat(user_id_str)
                await message.answer(f'Користувача @{user.username} додано до адмінів')
            else:
                await message.answer(f'Користувач @{user.username} вже є адміном')
        else:
            await message.answer('Такого користувача немає')
    else:
        await message.answer('Введено некоректний tg_id')


@router.message(Command('delete'))
async def add_admin(message: Message):
    from main import bot
    user_id_str = message.text[7:].strip()
    if user_id_str.isdigit():
        user_id = int(user_id_str)
        user_exist = await rq.get_user_by_user_id(user_id)
        if user_exist:
            user = await bot.get_chat(user_id_str)
            if user_exist.is_admin:
                await rq.delete_admin(user_id)
                user = await bot.get_chat(user_id_str)
                await message.answer(f'Користувача @{user.username} видалено з адмінів')
            else:
                await message.answer(f'Користувач @{user.username} НЕ є адміном')
        else:
            await message.answer('Такого користувача немає')
    else:
        await message.answer('Введено некоректний tg_id')

