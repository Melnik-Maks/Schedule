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

@router.callback_query(F.data == 'go_back_to_chat')
async def go_back_to_group(callback: CallbackQuery):
    await callback.answer('🔙 Ви повернулися назад')
    chat = await rq.get_chat_by_chat_id(callback.message.chat.id)
    await callback.message.edit_text(f'🎓 Ваша група: {chat.specialty}-{chat.course}{chat.group}')

@router.message(F.text == '🔄 Змінити групу')
async def reset_group(message: Message):
    is_user_in_group = await rq.user_has_group(message.from_user.id)
    await message.answer('🎓 Оберіть спеціальність:', reply_markup=await kb.specialties(is_user_in_group))

@router.message(F.text == '🔮 Обрати групу')
async def reset_group(message: Message):
    is_user_in_group = await rq.user_has_group(message.from_user.id)
    await message.answer('🎓 Оберіть вашу спеціальність:', reply_markup=await kb.specialties(is_user_in_group))


@router.callback_query(F.data.startswith('specialty'))
async def specialty(callback: CallbackQuery):
    if callback.message.chat.type == "private":
        user_group = await rq.user_has_group(callback.from_user.id)
        await callback.message.edit_text('🎓 Виберіть вашу спеціальність:', reply_markup=await kb.specialties(user_group))
    else:
        await callback.message.edit_text(f'🎓 Виберіть вашу спеціальність:',
                             reply_markup=await kb.specialties(add_button_go_back=True, is_chat=True))

@router.callback_query(F.data.startswith('course_'))
async def course(callback: CallbackQuery):
    await callback.message.edit_text('📚 Виберіть ваш курс:', reply_markup=await kb.courses(callback.data.split('_')[1]))

@router.callback_query(F.data.startswith('group_'))
async def group(callback: CallbackQuery):
    await callback.message.edit_text('👥 Виберіть вашу групу:', reply_markup=await kb.groups(
        callback.data.split('_')[1],
        callback.data.split('_')[2]
    ))

@router.callback_query(F.data.startswith('subgroup_'))
async def subgroup(callback: CallbackQuery):
    if callback.message.chat.type in ["group", "supergroup"]:
        chat = await rq.get_chat_by_chat_id(callback.message.chat.id)
        if chat:
            await rq.update_chat_group(callback.message.chat.id, await rq.get_group_id_by_group(callback.data.split("_")[1], callback.data.split("_")[2], callback.data.split("_")[3]))
            await callback.message.edit_text(f'✅ Вашу групу змінено на {callback.data.split("_")[1]}-{callback.data.split("_")[2]}{callback.data.split("_")[3]}')
        else:
            await rq.set_chat(callback.message.chat.id, await rq.get_group_id_by_group(callback.data.split("_")[1], callback.data.split("_")[2], callback.data.split("_")[3]))
            await callback.message.edit_text(f'📝 Вашу групу записано! Ваша група {callback.data.split("_")[1]}-{callback.data.split("_")[2]}{callback.data.split("_")[3]}')

    else:
        await callback.message.edit_text('🔢 Виберіть вашу підгрупу:', parse_mode='HTML', reply_markup=await kb.subgroups(
            callback.data.split('_')[1],
            callback.data.split('_')[2],
            callback.data.split('_')[3]
        ))

@router.callback_query(F.data.startswith('set_group_'))
async def set_user_group(callback: CallbackQuery):
    if await rq.user_has_group(callback.from_user.id):
        await callback.message.edit_text(f'📌 Вашу групу змінено')
        await callback.message.answer(f'🎓 Ваша нова група: {callback.data.split("_")[2]}',
                                        reply_markup=await kb.profile(callback.from_user.id))
    else:
        await callback.message.edit_text(f'✅ Вашу групу записано')
        await callback.message.answer(f'🎓 Ваша група: {callback.data.split("_")[2]}', reply_markup=await kb.menu(callback.from_user.id))
    await rq.set_user_group(callback.from_user.id, callback.data.split('_')[2])

