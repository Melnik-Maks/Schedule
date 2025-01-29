from gc import callbacks
import asyncio

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from cachetools.func import mru_cache

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
async def group_command(message: Message):
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
    if message.from_user.id == 722714127:
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
    if message.from_user.id == 722714127:
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

@router.message(Command('set_schedule'))
async def add_admin(message: Message):
    if message.from_user.id == 722714127:
        await message.answer('🕒Це займе деякий час...')

        #await message.edit_text(f"Завантаження... ⏳")

        await rq.set_groups()
        await rq.clear_schedule()
        await rq.set_schedule()

        await message.answer('Розклад успішно перезаписано ✅')

@router.message(Command('set_sticker'))
async def set_sticker(message: Message):
    sticker_id = message.text.split()[1]
    if message.from_user.id == 722714127:
        await rq.set_user_sticker(message.from_user.id, sticker_id)
        await message.answer('Ваш стікер змінено 🦠')

@router.message(Command('get_users'))
async def get_users(message: Message):
    from main import bot
    if message.from_user.id == 722714127:
        groups = await rq.get_groups()
        for group in groups:
            users = await rq.get_users_by_groups(group.id)
            text = f'<b>{group.specialty}-{group.course}{group.group}</b> ({len(users)} користувачів)\n'
            for user in users:
                chat = await bot.get_chat(user.tg_id)
                text += f'@{chat.username}\n'
            await message.answer(text, parse_mode='HTML')

