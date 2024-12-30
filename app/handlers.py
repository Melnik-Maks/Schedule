from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
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
        await message.answer('Спочатку виберіть свою групу ;)\nВиберіть вашу спецвальність', reply_markup=await kb.specialties())
    else:
        await message.answer('Можете переглянути розклад', reply_markup=kb.schedule)

@router.message(F.text == 'Змінити групу')
async def reset_group(message: Message):
    await message.answer('Виберіть спецвальність', reply_markup=await kb.specialties())

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
    await callback.message.edit_text('Дякуємо, вашу групу записано!')
    await callback.message.answer('Можете переглянути розклад', reply_markup=kb.schedule)

@router.message(F.text == 'Розклад')
async def schedule(message: Message):
    await message.answer('Виберіть день', reply_markup=await kb.days())

@router.message(F.text == 'Розклад на сьогодні')
async def schedule_for_today(message: Message):
    day_number = message.date.weekday()
    if day_number == 6:
        await message.answer('В неділю пар немає ;)')
    else:
        day = config.daysOfTheWeek[day_number]
        list_of_pairs_for_day = await rq.get_schedule_by_day(day, message.from_user.id)
        await send_schedule(message, day, list_of_pairs_for_day)


@router.callback_query(F.data == 'schedule')
async def week(callback: CallbackQuery):
    await callback.message.answer('Виберіть день', reply_markup=await kb.days())

@router.callback_query(F.data.startswith('day_'))
async def schedule_for_day(callback: CallbackQuery):
    day = callback.data.split('_')[1]
    list_of_pairs_for_day = await rq.get_schedule_by_day(day, callback.from_user.id)
    await send_schedule(callback, day, list_of_pairs_for_day)
    '''
    await callback.message.answer(f"{bold('Розклад')} за {bold(day1)}:\n", parse_mode="Markdown")
    if not schedule:
        await callback.message.answer('На це день немає пар :)')
    else:
        for i in schedule_for_day:
            subject_info = (
                f"{bold('Предмет:')} {i.subject}\n"
                f"{bold('Час:')} {i.time}\n"
                f"{bold('Тип заняття:')} {italic(i.type)}\n"
                f"{bold('Викладач:')} {i.teacher}\n"
                f"{bold('Аудиторія:')} {i.room}\n"
                f"{bold('Тижні:')} {i.weeks}\n"
            )

            if i.type.lower() == "лекція":
                subject_info += f"{bold('Zoom:')} {i.zoom_link}\n"

            await callback.message.answer(subject_info, parse_mode="Markdown")
    '''
    await callback.message.answer('Виберіть день', reply_markup=await kb.days())


@router.message(Command('overwrite'))
async def overwriting():
    await rq.set_db()
