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
from app.database.requests import user_has_group, get_user_group_id_by_tg_id
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
async def group(message: Message):
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

@router.callback_query(F.data == 'go_back_to_chat')
async def go_back_to_group(callback: CallbackQuery):
    await callback.answer('🔙 Ви повернулися назад')
    chat = await rq.get_chat_by_chat_id(callback.message.chat.id)
    await callback.message.edit_text(f'🎓 Ваша група: {chat.specialty}-{chat.course}{chat.group}')

@router.message(F.text == '🔄 Змінити групу')
async def reset_group(message: Message):
    is_user_in_group = await user_has_group(message.from_user.id)
    await message.answer('🎓 Оберіть спеціальність:', reply_markup=await kb.specialties(is_user_in_group))

@router.message(F.text == '🔮 Обрати групу')
async def reset_group(message: Message):
    is_user_in_group = await user_has_group(message.from_user.id)
    await message.answer('🎓 Оберіть вашу спеціальність:', reply_markup=await kb.specialties(is_user_in_group))

@router.callback_query(F.data == 'profile')
async def go_back_to_profile(callback: CallbackQuery):
    await callback.answer('🔙 Ви повернулися в профіль')
    user = callback.from_user

    profile_text = (
        f"👤 <b>Ваш профіль</b>\n\n"

        f"⚡️ <b>Ім'я:</b> {user.first_name}\n"
        f"📛 <b>Юзернейм:</b> @{user.username}\n"
        f"🆔 <b>ID користувача:</b> {user.id}\n"
        f"🏫 <b>Група:</b> {await rq.get_group_title_by_id(await rq.get_user_group_id_by_tg_id(user.id))}\n"
    )
    await callback.message.edit_text(profile_text, parse_mode='HTML')


@router.callback_query(F.data.startswith('specialty'))
async def specialty(callback: CallbackQuery):
    if callback.message.chat.type == "private":
        user_group = await user_has_group(callback.from_user.id)
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
            await rq.update_chat_group(callback.message.chat.id, callback.data.split("_")[1], callback.data.split("_")[2], callback.data.split("_")[3])
            await callback.message.edit_text(f'✅ Вашу групу змінено на {callback.data.split("_")[1]}-{callback.data.split("_")[2]}{callback.data.split("_")[3]}')
        else:
            await rq.set_chat(callback.message.chat.id, callback.data.split("_")[1], callback.data.split("_")[2], callback.data.split("_")[3])
            await callback.message.edit_text(f'📝 Вашу групу записано! Ваша група {callback.data.split("_")[1]}-{callback.data.split("_")[2]}{callback.data.split("_")[3]}')

    else:
        await callback.message.edit_text('🔢 Виберіть вашу підгрупу:', parse_mode='HTML', reply_markup=await kb.subgroups(
            callback.data.split('_')[1],
            callback.data.split('_')[2],
            callback.data.split('_')[3]
        ))

@router.callback_query(F.data.startswith('setGroup_'))
async def set_user_group(callback: CallbackQuery):
    if await rq.user_has_group(callback.from_user.id):
        await callback.message.edit_text(f'📌 Вашу групу змінено')
        await callback.message.answer(f'🎓 Ваша нова група: {callback.data.split("_")[1]}',
                                        reply_markup=await kb.profile(callback.from_user.id))
    else:
        await callback.message.edit_text(f'✅ Вашу групу записано')
        await callback.message.answer(f'🎓 Ваша група: {callback.data.split("_")[1]}', reply_markup=await kb.menu(callback.from_user.id))
    await rq.set_user_group(callback.from_user.id, callback.data.split('_')[1])

@router.message(F.text == '📆 Розклад')
async def schedule(message: Message):
    is_member = await rq.user_has_group(message.from_user.id)
    if is_member:
        await message.answer('🗂 Оберіть опцію з розкладом ', reply_markup=kb.schedule)
    else:
        await message.answer('<b>Спочатку обери свою групу 😉</b>', parse_mode='HTML')
        await message.answer(f'🎓 Виберіть вашу спеціальність:', reply_markup=await kb.specialties(add_button_go_back=is_member))

@router.message(F.text == '👤 Профіль')
async def profile(message: Message):
    user = message.from_user

    profile_text = (
        f"👤 <b>Ваш профіль</b>\n\n"
        
        f"⚡️ <b>Ім'я:</b> {user.first_name}\n"
        f"📛 <b>Юзернейм:</b> @{user.username}\n"
        f"🆔 <b>ID користувача:</b> {user.id}\n"
        f"🏫 <b>Група:</b> {await rq.get_group_title_by_id(await rq.get_user_group_id_by_tg_id(user.id))}\n"
    )

    await message.answer(profile_text, parse_mode="HTML", reply_markup=await kb.profile(message.from_user.id))

@router.message(F.text == '🏠 Додому')
async def schedule_for_week(message: Message):
    await message.answer('🪬 Ви повернулися в меню', reply_markup=await kb.menu(message.from_user.id))

@router.message(F.text == '🛠 Змінити розклад 🛠')
async def update_schedule(message: Message):
    if await rq.is_admin(message.from_user.id):
        await message.answer('Тут можна оновити розклад з exel', reply_markup=kb.update_schedule(message.from_user.id))
    else:
        await message.answer('Це може зробити тільки адмін')

@router.message(F.text == '🧲 Перезаписати весь розклад 🧲')
async def set_schedule(message: Message):
    if message.from_user.id == 722714127:
        await message.answer('Попередній розклад буде видалений, ви впевнені?', reply_markup=kb.ask_to_update_all_schedule())
    else:
        await message.answer(f'Це може зробити тільки адмін')

@router.message(F.text == '🔁 Оновити розклад 🔁')
async def update_schedule(message: Message):
    if await rq.is_admin(message.from_user.id):
        group_title = await rq.get_group_title_by_user_id(message.from_user.id)
        await message.answer(f'Ви справді хочете оновити розклад для {group_title[:-2]}?', reply_markup=kb.ask_to_update_schedule_for_one_group())
    else:
        await message.answer('Це може зробити тільки адмін')

@router.message(F.text == '🖋 Редагувати розклад 🖋')
async def set_schedule(message: Message):
    if await rq.is_admin(message.from_user.id):
        await message.answer('Тут можна редагувати розклад в exel', reply_markup=kb.schedule_in_exel(await rq.get_sheet_id_by_user_id(message.from_user.id)))
    else:
        await message.answer('Це може зробити тільки адмін')

@router.callback_query(F.data.startswith('update_all_schedule_'))
async def ask_yes_or_no(callback: CallbackQuery):
    result = callback.data.split('_')[-1]
    if result == 'yes':
        await callback.answer('🕒Це займе деякий час...')
        await rq.set_groups()
        await rq.clear_schedule()
        await rq.set_schedule()
        await callback.message.edit_text('Розклад заповнено')

    else:
        await callback.message.edit_text('Ви повернулися назад')
        await callback.answer('Ви повернулися назад')

@router.callback_query(F.data.startswith('update_schedule_for_one_group_'))
async def ask_yes_or_no(callback: CallbackQuery):
    result = callback.data.split('_')[-1]
    if result == 'yes':
        group_title = await rq.get_group_title_by_user_id(callback.from_user.id)
        await callback.answer('🕒Це займе деякий час...')
        await rq.set_groups()
        await rq.clear_all_subgroups_by_group(group_title)
        await rq.set_all_subgroups_by_group(group_title)
        await callback.message.edit_text(f'Розклад заповнено для {group_title[:-2]}')

    else:
        await callback.message.edit_text('Ви повернулися назад')
        await callback.answer('Ви повернулися назад')



@router.message(F.text == '📜 Оригінальний розклад')
async def schedule_for_week(message: Message):
    await message.answer('🧷 Ось оригінальний розклад: ', reply_markup=kb.original_schedule)

@router.message(F.text == '📆 Розклад на тиждень')
async def schedule_for_week(message: Message):
    await message.answer('📅 Виберіть день', reply_markup=await kb.days())

@router.message(F.text == '📅 Сьогодні')
async def schedule_for_today(message: Message):
    day_number = message.date.weekday()
    if day_number == 6:
        await message.answer_sticker(
            "CAACAgIAAxUAAWd60zJyaJFXLJvhFaxCIq00nZ9DAALAUgACLiKgSoppqBV05QeNNgQ"
        )
        await message.answer('😌 В неділю пар немає ;)')
    else:
        day = config.daysOfTheWeek[day_number]
        list_of_pairs_for_day = await rq.get_schedule_by_day(day, message.from_user.id)
        await send_schedule(message, day, list_of_pairs_for_day, False, 1)

@router.message(F.text == '📅 Завтра')
async def schedule_for_tomorrow(message: Message):
    day_number = (message.date.weekday() + 1) % 7
    if day_number == 6:
        await message.answer_sticker(
            "CAACAgIAAxUAAWd60zJyaJFXLJvhFaxCIq00nZ9DAALAUgACLiKgSoppqBV05QeNNgQ"
        )
        await message.answer('😌 В неділю пар немає ;)')
    else:
        day = config.daysOfTheWeek[day_number]
        list_of_pairs_for_day = await rq.get_schedule_by_day(day, message.from_user.id)
        await send_schedule(message, day, list_of_pairs_for_day, False, 2)


@router.message(F.text == '🔔 Вимкнути нагадування')
async def turn_off_reminders(message: Message):
    await rq.turn_off_reminders(message.from_user.id)
    await message.answer('🔕 Нагадування про пари вимкнено!', reply_markup=await kb.profile(message.from_user.id))


@router.message(F.text == '🔕 Увімкнути нагадування')
async def turn_on_reminders(message: Message):
    await rq.turn_on_reminders(message.from_user.id)
    await message.answer('🔔 Нагадування про пари увімкнено!', reply_markup=await kb.profile(message.from_user.id))

@router.callback_query(F.data.startswith('day_'))
async def schedule_for_day(callback: CallbackQuery):
    await callback.answer('')
    day = callback.data.split('_')[1]
    list_of_pairs_for_day = await rq.get_schedule_by_day(day, callback.from_user.id)
    await send_schedule(callback, day, list_of_pairs_for_day, True)

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
