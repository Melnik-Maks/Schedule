from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.markdown import bold, italic, code
from aiogram.fsm.context import FSMContext
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
    await message.answer('Hello!', reply_markup=kb.main)

@router.message(F.text == 'Розклад')
async def week(message: Message):
    await message.answer('Виберіть групу', reply_markup=await kb.groups())


@router.callback_query(F.data.startswith('group_'))
async def group(callback: CallbackQuery):
    await callback.message.answer('Виберіть підгрупу', reply_markup=await kb.subgroups(callback.data.split('_')[1]))

@router.callback_query(F.data.startswith('subgroup_'))
async def subgroup(callback: CallbackQuery):
    await callback.message.answer('Виберіть день', reply_markup=await kb.days(callback.data.split('_')[1]))

@router.callback_query(F.data.startswith('day_'))
async def day(callback: CallbackQuery):
    schedule = await rq.get_schedule_by_day(callback.data.split('_')[1])
    day1, group1, subgroup1 = callback.data.split('_')[1].split('/')
    await callback.message.answer(f"{bold('Розклад')} за {bold(day1)} для {group1}/{subgroup1}:\n", parse_mode="Markdown")

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
    await callback.message.answer('Виберіть день', reply_markup=await kb.days(f"{group1}/{subgroup1}"))


@router.message(Command('overwrite'))
async def overwriting():
    await rq.set_db()
