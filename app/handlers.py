from gc import callbacks

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.markdown import bold, italic, code
from aiogram.fsm.context import FSMContext
from pyasn1_modules.rfc8018 import algid_hmacWithSHA1
from sqlalchemy.util import await_fallback


import app.keyboards as kb
import app.database.requests as rq
import config
from app.utils import send_schedule

router = Router()

class Reg(StatesGroup):
    name = State()
    number = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    is_member = await rq.user_has_group(message.from_user.id)
    if not is_member:
        await message.answer('Привіт, це бот щоб зручно переглядати розклад :)')
        await message.answer('Спочатку виберіть свою групу ;)\nВиберіть вашу спецвальність', reply_markup=await kb.specialties_for_start())
    else:
        await message.answer('Виберіть', reply_markup=kb.menu)

@router.message(F.text == 'Змінити групу')
async def reset_group(message: Message):
    await message.answer('Виберіть спецвальність', reply_markup=await kb.specialties())

@router.callback_query(F.data.startswith('goback_menu'))
async def go_back_to_group(callback: CallbackQuery):
    await callback.answer('Ви повернулися в меню')
    await callback.message.edit_text('Меню')

@router.callback_query(F.data.startswith('reset_group'))
async def reset_group1(callback: CallbackQuery):
    await callback.message.answer('Виберіть спецвальність', reply_markup=await kb.specialties())

@router.callback_query(F.data.startswith('specialty_'))
async def group(callback: CallbackQuery):
    await callback.message.edit_text('Виберіть вашу групу', reply_markup=await kb.groups(callback.data.split('_')[1]))

@router.callback_query(F.data.startswith('goback_specialty'))
async def go_back_to_specialty(callback: CallbackQuery):
    await callback.message.edit_text('Виберіть спецвальність', reply_markup=await kb.specialties())

@router.callback_query(F.data.startswith('group_'))
async def subgroup(callback: CallbackQuery):
    await callback.message.edit_text('Виберіть вашу підгрупу', reply_markup=await kb.subgroups(callback.data.split('_')[1]))

@router.callback_query(F.data.startswith('goback_group'))
async def go_back_to_group(callback: CallbackQuery):
    await callback.message.edit_text('Виберіть вашу групу', reply_markup=await kb.groups(callback.data.split('_')[2]))

@router.callback_query(F.data.startswith('subgroup_'))
async def set_user_group(callback: CallbackQuery):
    await rq.update_user_group(callback.from_user.id, callback.data.split('_')[1])
    await callback.message.edit_text('Дякуємо, вашу групу записано.')
    await callback.message.answer(f'Ваша група {callback.data.split("_")[1]}', reply_markup=kb.menu)

@router.message(F.text == 'Розклад')
async def schedule(message: Message):
    await message.answer('Оберіть опцію: ', reply_markup=kb.schedule)

@router.callback_query(F.data == 'schedule_for_week')
async def schedule_for_week(callback: CallbackQuery):
    await callback.message.edit_text('Виберіть день', reply_markup=await kb.days())

@router.callback_query(F.data == 'schedule_for_today')
async def schedule_for_today(callback: CallbackQuery):
    day_number = callback.message.date.weekday()
    if day_number == 6:
        await callback.message.answer('В неділю пар немає ;)')
    else:
        day = config.daysOfTheWeek[day_number]
        list_of_pairs_for_day = await rq.get_schedule_by_day(day, callback.from_user.id)
        await send_schedule(callback.message, day, list_of_pairs_for_day)


@router.callback_query(F.data.startswith('day_'))
async def schedule_for_day(callback: CallbackQuery):
    await callback.answer('')
    day = callback.data.split('_')[1]
    list_of_pairs_for_day = await rq.get_schedule_by_day(day, callback.from_user.id)
    await send_schedule(callback, day, list_of_pairs_for_day)
    await callback.message.answer('Виберіть день', reply_markup=await kb.days())


@router.message(Command('overwrite'))
async def overwriting():
    await rq.set_db()
