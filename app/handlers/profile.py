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


@router.message(F.text == '👤 Профіль')
async def profile(message: Message):
    user = message.from_user
    await message.answer_sticker(await rq.get_user_sticker_id(user.id))
    profile_text = (
        f"👤 <b>Ваш профіль</b>\n\n"

        f"⚡️ <b>Ім'я:</b> {user.first_name}\n"
        f"📛 <b>Юзернейм:</b> @{user.username}\n"
        f"🆔 <b>ID користувача:</b> <code>{user.id}</code>\n"
        f"🏫 <b>Група:</b> {await rq.get_group_title_by_id(await rq.get_user_group_id_by_tg_id(user.id))}/{await rq.get_user_subgroup_by_user_id(user.id)}\n"
    )

    await message.answer(profile_text, parse_mode="HTML", reply_markup=await kb.profile(message.from_user.id))

@router.callback_query(F.data == 'profile')
async def go_back_to_profile(callback: CallbackQuery):
    await callback.answer('🔙 Ви повернулися в профіль')
    user = callback.from_user

    profile_text = (
        f"👤 <b>Ваш профіль</b>\n\n"

        f"⚡️ <b>Ім'я:</b> {user.first_name}\n"
        f"📛 <b>Юзернейм:</b> @{user.username}\n"
        f"🆔 <b>ID користувача:</b> <code>{user.id}</code>\n"
        f"🏫 <b>Група:</b> {await rq.get_group_title_by_id(await rq.get_user_group_id_by_tg_id(user.id))}/{await rq.get_user_subgroup_by_user_id(user.id)}\n"
    )
    await callback.message.edit_text(profile_text, parse_mode='HTML')

@router.message(F.text == '🏂 Список всіх адмінів')
async def list_of_all_admins(message: Message):
    from main import bot
    admins = await rq.get_all_admins()
    for admin in admins:
        user = await bot.get_chat(admin.tg_id)
        await message.answer(f'@{user.username} - {await rq.get_group_title_by_id(admin.group_id)}')

@router.message(F.text == '☣️ Додати')
async def list_of_all_admins(message: Message):
    await message.answer(f'Введіть команду <code>/add</code> ...  вказавши ID користувача', parse_mode='HTML')

@router.message(F.text == '⛔️ Видалити')
async def list_of_all_admins(message: Message):
    await message.answer('Введіть команду <code>/delete</code> ...  вказавши ID користувача', parse_mode='HTML')

@router.message(F.text == '🔔 Вимкнути нагадування')
async def turn_off_reminders(message: Message):
    await rq.turn_off_reminders(message.from_user.id)
    await message.answer('🔕 Нагадування про пари вимкнено!', reply_markup=await kb.profile(message.from_user.id))

@router.message(F.text == '🔕 Увімкнути нагадування')
async def turn_on_reminders(message: Message):
    await rq.turn_on_reminders(message.from_user.id)
    await message.answer('🔔 Нагадування про пари увімкнено!', reply_markup=await kb.profile(message.from_user.id))

