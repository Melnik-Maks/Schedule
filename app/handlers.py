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

router = Router()

class Reg(StatesGroup):
    name = State()
    number = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Привіт, це бот щоб зручно переглядати розклад :)')
    await message.answer('Спочатку введи свою групу ;)')
    await message.answer('Виберіть вашу спецвальність', reply_markup=await kb.specialties())


@router.callback_query(F.data.startswith('specialty_'))
async def group(callback: CallbackQuery):
    await callback.message.edit_text('Виберіть вашу групу', reply_markup=await kb.groups(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('group_'))
async def subgroup(callback: CallbackQuery):
    await callback.message.edit_text('Виберіть вашу підгрупу', reply_markup=await kb.subgroups(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('subgroup_'))
async def set_user_group(callback: CallbackQuery):
    await rq.update_user_group(callback.from_user.id, callback.data.split('_')[1])
    await callback.message.edit_text('Дякуємо, вашу групу записано!')
    await callback.message.answer('Можете переглянути розклад', reply_markup=kb.schedule)


@router.callback_query(F.data == 'schedule')
async def week(callback: CallbackQuery):
    await callback.message.answer('Виберіть день', reply_markup=await kb.days())

@router.callback_query(F.data.startswith('day_'))
async def day(callback: CallbackQuery):
    day1 = callback.data.split('_')[1]
    schedule = await rq.get_schedule_by_day(day1, callback.from_user.id)
    await callback.message.answer(f"{bold('Розклад')} за {bold(day1)}:\n", parse_mode="Markdown")

    for i in schedule:
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
    await callback.message.answer('Виберіть день', reply_markup=await kb.days())


@router.message(Command('overwrite'))
async def overwriting():
    await rq.set_db()
