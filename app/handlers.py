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
        await message.answer('Спочатку виберіть свою групу ;)\nВиберіть вашу спецвальність', reply_markup=await kb.specialties(is_member))
    else:
        await message.answer('Виберіть', reply_markup=kb.menu1)

@router.message(F.text == 'Змінити групу')
async def reset_group(message: Message):
    await message.answer('Виберіть спецвальність', reply_markup=await kb.specialties())

@router.callback_query(F.data.startswith('goback_menu'))
async def go_back_to_group(callback: CallbackQuery):
    await callback.answer('Ви повернулися в профіль')
    await callback.message.edit_text('Ваш профіль')

@router.callback_query(F.data.startswith('reset_group'))
async def reset_group1(callback: CallbackQuery):
    await callback.message.answer('Виберіть спецвальність', reply_markup=await kb.specialties())

@router.callback_query(F.data.startswith('specialty_'))
async def group(callback: CallbackQuery):
    await callback.message.edit_text('Виберіть вашу групу', reply_markup=await kb.groups(callback.data.split('_')[1]))

@router.callback_query(F.data.startswith('goback_specialty'))
async def go_back_to_specialty(callback: CallbackQuery):
    is_member = await rq.user_has_group(callback.from_user.id)
    await callback.message.edit_text('Виберіть спецвальність', reply_markup=await kb.specialties(is_member))

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
    await callback.message.answer(f'Ваша група {callback.data.split("_")[1]}', reply_markup=kb.menu1)

@router.message(F.text == 'Розклад1')
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

@router.message(F.text == 'Розклад')
async def schedule(message: Message):
    await message.answer('Оберіть опцію: ', reply_markup=kb.schedule1)

@router.message(F.text == 'Профіль')
async def schedule(message: Message):
    await message.answer('Ваш профіль: ', reply_markup=kb.profile)

@router.message(F.text == 'Інформація про тебе')
async def info_about_you(message: Message):
    user = message.from_user
    response = (
        f"Ваше ім'я: {user.first_name}\n"
        f"Ваше прізвище: {user.last_name or 'не вказано'}\n"
        f"Ваш юзернейм: @{user.username or 'не вказано'}\n"
        f"Ваш ID: {user.id}\n"
        f"Ваша група: {await rq.get_group_title_by_id(await rq.get_user_group_id_by_tg_id(user.id))}"
    )
    await message.answer(response)

@router.message(F.text == 'Додому')
async def schedule_for_week(message: Message):
    await message.answer('Ви повернулися в меню', reply_markup=kb.menu1)

@router.message(F.text == 'Оригінальний розклад')
async def schedule_for_week(message: Message):
    await message.answer('Ось оригінальний розклад: ', reply_markup=kb.original_schedule)

@router.message(F.text == 'Розклад на тиждень')
async def schedule_for_week(message: Message):
    await message.answer('Виберіть день', reply_markup=await kb.days())

@router.message(F.text == 'Сьогодні')
async def schedule_for_today(message: Message):
    day_number = message.date.weekday()
    if day_number == 6:
        await message.answer('В неділю пар немає ;)')
    else:
        day = config.daysOfTheWeek[day_number]
        list_of_pairs_for_day = await rq.get_schedule_by_day(day, message.from_user.id)
        await send_schedule(message, day, list_of_pairs_for_day)

@router.message(F.text == 'Завтра')
async def schedule_for_today(message: Message):
    day_number = (message.date.weekday() + 1) % 7
    if day_number == 6:
        await message.answer('В неділю пар немає ;)')
    else:
        day = config.daysOfTheWeek[day_number]
        list_of_pairs_for_day = await rq.get_schedule_by_day(day, message.from_user.id)
        await send_schedule(message, day, list_of_pairs_for_day)

@router.callback_query(F.data.startswith('day_'))
async def schedule_for_day(callback: CallbackQuery):
    await callback.answer('')
    day = callback.data.split('_')[1]
    list_of_pairs_for_day = await rq.get_schedule_by_day(day, callback.from_user.id)
    await send_schedule(callback, day, list_of_pairs_for_day)
    #await callback.message.answer('Виберіть день', reply_markup=await kb.days())


@router.message(Command('overwrite'))
async def overwriting():
    await rq.set_db()
