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


@router.message(F.text == '🤿 Адміни')
async def set_schedule(message: Message):
    if message.from_user.id == 722714127:
        await message.answer_sticker("CAACAgIAAxUAAWd60zJ95DTj3m7st3mKfNLHMpgpAAL8YQACLV-hSnFMBpVtgy_NNgQ")
        await message.answer('Тут можна видалити або додати адмінів', reply_markup=await kb.admins())
    else:
        await message.answer(f'Ви не маєте доступу')

@router.message(F.text == '🏠 Додому')
async def schedule_for_week(message: Message):
    await message.answer_sticker("CAACAgIAAxUAAWd60zJT-ffa4d6WVmN-FAJsmgABkQACI1sAAnjXoEo52beO77VqaTYE")
    await message.answer('🪬 Ви повернулися в меню', reply_markup=await kb.menu(message.from_user.id))

@router.message(F.text == '⚜️ Підтримка ⚜️')
async def support(message: Message):
    await message.answer_sticker(
        "CAACAgIAAxkBAAIFe2d60JdzM4YRAdwlYigzUHi3alC9AAI8XwACDQOgSnN2ylbRRSMaNgQ",
        reply_markup=kb.support_button
    )

@router.message(F.sticker)
async def get_sticker_id(message: Message):
    sticker = message.sticker
    await message.reply(f"'{sticker.file_id}',")