from gc import callbacks

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
from app.database.requests import user_has_group
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
        await message.answer('Виберіть', reply_markup=kb.menu)

@router.message(F.text == '🔄 Змінити групу')
async def reset_group(message: Message):
    user_group = await user_has_group(message.from_user.id)
    await message.answer('Виберіть спеціальність', reply_markup=await kb.specialties(user_group))

@router.callback_query(F.data.startswith('settings'))
async def go_back_to_group(callback: CallbackQuery):
    await callback.answer('Ви повернулися до налаштувань')
    await callback.message.edit_text('Налаштування профілю')

@router.callback_query(F.data.startswith('specialty'))
async def course(callback: CallbackQuery):
    user_group = await user_has_group(callback.from_user.id)
    await callback.message.edit_text('Виберіть спецвальність', reply_markup=await kb.specialties(user_group))

@router.callback_query(F.data.startswith('course_'))
async def course(callback: CallbackQuery):
    await callback.message.edit_text('Виберіть ваш курс', reply_markup=await kb.courses(callback.data.split('_')[1]))

@router.callback_query(F.data.startswith('group_'))
async def group(callback: CallbackQuery):
    await callback.message.edit_text('Виберіть вашу групу', reply_markup=await kb.groups(
        callback.data.split('_')[1],
        callback.data.split('_')[2]
    ))

@router.callback_query(F.data.startswith('subgroup_'))
async def subgroup(callback: CallbackQuery):
    await callback.message.edit_text('Виберіть вашу підгрупу', reply_markup=await kb.subgroups(
        callback.data.split('_')[1],
        callback.data.split('_')[2],
        callback.data.split('_')[3]
    ))

@router.callback_query(F.data.startswith('setGroup_'))
async def set_user_group(callback: CallbackQuery):
    if await rq.user_has_group(callback.from_user.id):
        await rq.update_user_group(callback.from_user.id, callback.data.split('_')[1])
        await callback.message.edit_text(f'Дякуємо, вашу групу змінено.')
        await callback.message.answer(f'Ваша нова група {callback.data.split("_")[1]}',
                                         reply_markup=kb.settings)
    else:
        await rq.update_user_group(callback.from_user.id, callback.data.split('_')[1])
        await callback.message.edit_text(f'Дякуємо, вашу групу записано.')
        await callback.message.answer(f' Ваша група {callback.data.split("_")[1]}',
                                         reply_markup=kb.menu)

@router.message(F.text == '📅 Розклад')
async def schedule(message: Message):
    await message.answer('Оберіть опцію: ', reply_markup=kb.schedule)

@router.message(F.text == '👤 Профіль')
async def schedule(message: Message):
    user = message.from_user

    profile_text = (
        f"👤 <b>Ваш профіль</b>\n\n"
        
        f"⚡️ <b>Ім'я:</b> {user.first_name}\n"
        f"📛 <b>Нікнейм:</b> @{user.username}\n"
        f"🆔 <b>ID користувача:</b> {user.id}\n"
        f"🏫 <b>Група:</b> {await rq.get_group_title_by_id(await rq.get_user_group_id_by_tg_id(user.id))}\n"
    )

    await message.answer(profile_text, parse_mode="HTML", reply_markup=kb.profile)

@router.message(F.text == '🏠 Додому')
async def schedule_for_week(message: Message):
    await message.answer('Ви повернулися в меню', reply_markup=kb.menu)

@router.message(F.text == '📜 Оригінальний розклад')
async def schedule_for_week(message: Message):
    await message.answer('Ось оригінальний розклад: ', reply_markup=kb.original_schedule)

@router.message(F.text == '🗓️ Розклад на тиждень')
async def schedule_for_week(message: Message):
    await message.answer('Виберіть день', reply_markup=await kb.days())

@router.message(F.text == '📆 Сьогодні')
async def schedule_for_today(message: Message):
    day_number = message.date.weekday()
    if day_number == 6:
        await message.answer('В неділю пар немає ;)')
    else:
        day = config.daysOfTheWeek[day_number]
        list_of_pairs_for_day = await rq.get_schedule_by_day(day, message.from_user.id)
        await send_schedule(message, day, list_of_pairs_for_day, False, 1)

@router.message(F.text == '📆 Завтра')
async def schedule_for_tomorrow(message: Message):
    day_number = (message.date.weekday() + 1) % 7
    if day_number == 6:
        await message.answer('В неділю пар немає ;)')
    else:
        day = config.daysOfTheWeek[day_number]
        list_of_pairs_for_day = await rq.get_schedule_by_day(day, message.from_user.id)
        await send_schedule(message, day, list_of_pairs_for_day, False, 2)


@router.message(F.text == '🔔 Вимкнути нагадування')
async def turn_off_reminders(message: Message):
    await rq.turn_off_reminders(message.from_user.id)
    await message.answer('🔕 Нагадування про пари вимкнено!', reply_markup=kb.settings_with_disable_reminders)


@router.message(F.text == '🔕 Увімкнути нагадування')
async def turn_on_reminders(message: Message):
    await rq.turn_on_reminders(message.from_user.id)
    await message.answer('🔔 Нагадування про пари увімкнено!', reply_markup=kb.settings_with_enable_reminders)

@router.callback_query(F.data.startswith('day_'))
async def schedule_for_day(callback: CallbackQuery):
    await callback.answer('')
    day = callback.data.split('_')[1]
    list_of_pairs_for_day = await rq.get_schedule_by_day(day, callback.from_user.id)
    await send_schedule(callback, day, list_of_pairs_for_day, True)

@router.message(F.text == '⚙️ Налаштування')
async def support(message: Message):
    if await rq.get_user_reminder(message.from_user.id):
        await message.answer(
            'Налаштування профілю',
            reply_markup=kb.settings_with_enable_reminders
        )
    else:
        await message.answer(
            'Налаштування профілю',
            reply_markup=kb.settings_with_disable_reminders
        )

@router.message(F.text == '⚜️ Підтримка ⚜️')
async def support(message: Message):
    await message.answer_sticker(
        "CAACAgIAAxkBAAIFe2d60JdzM4YRAdwlYigzUHi3alC9AAI8XwACDQOgSnN2ylbRRSMaNgQ",
        reply_markup=kb.support_button
    )

    '''sticker_pack_name = "StickerStar0132_by_e4zybot"

    try:
        sticker_set = await message.bot.get_sticker_set(sticker_pack_name)
        random_sticker = random.choice(sticker_set.stickers)

        await message.answer_sticker(random_sticker.file_id, reply_markup=kb.support_button)

    except Exception as e:
        await message.reply(f"Не вдалося отримати стікер: {e}")'''

@router.message(F.sticker)
async def get_sticker_id(message: Message):
    sticker = message.sticker
    await message.reply(f"File ID цього стікера: {sticker.file_id}")


@router.message(Command('overwrite'))
async def overwriting():
    await rq.set_db()
