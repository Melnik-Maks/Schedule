from gc import callbacks
import asyncio

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove



import app.keyboards as kb
import app.database.requests as rq
import config
from app.utils import send_schedule


router = Router()

@router.message(F.text == '📆 Розклад')
async def schedule(message: Message):
    is_member = await rq.user_has_group(message.from_user.id)
    if is_member:
        await message.answer_sticker("CAACAgIAAxUAAWd60zJKpj93j9KTbfNTgYEKVJTVAAKWWgACYZqhSrZRv5jw2QdhNgQ", reply_markup=await kb.schedule(message.from_user.id))
        #await message.answer('🗂 Оберіть опцію з розкладом ', reply_markup=await kb.schedule(message.from_user.id))
        await message.answer('📅 Виберіть день', reply_markup=await kb.days())
    else:
        await message.answer('<b>Спочатку обери свою групу 😉</b>', parse_mode='HTML')
        await message.answer(f'🎓 Виберіть вашу спеціальність:', reply_markup=await kb.specialties(add_button_go_back=is_member))

@router.message(F.text == '🛠 Змінити розклад 🛠')
async def update_schedule(message: Message):
    if await rq.is_admin(message.from_user.id):
        await message.answer('✏️ Тут можна оновити розклад', reply_markup=kb.update_schedule(message.from_user.id))
    else:
        await message.answer('Це може зробити тільки адмін')

@router.message(F.text == '🧲 Перезаписати весь розклад 🧲')
async def set_schedule(message: Message):
    if message.from_user.id == 722714127:
        await message.answer('🤖 Попередній розклад буде видалений, ви впевнені?', reply_markup=kb.ask_to_update_all_schedule())
    else:
        await message.answer(f'🔎 Це може зробити тільки адмін')

@router.message(F.text == '🔁 Оновити розклад 🔁')
async def update_schedule(message: Message):
    if await rq.is_admin(message.from_user.id):
        group_title = await rq.get_group_title_by_user_id(message.from_user.id)
        await message.answer(f'🧐 Ви справді хочете оновити розклад для {group_title}?', reply_markup=kb.ask_to_update_schedule_for_one_group())
    else:
        await message.answer('🔎 Це може зробити тільки адмін')

@router.message(F.text == '🖋 Редагувати розклад 🖋')
async def set_schedule(message: Message):
    if await rq.is_admin(message.from_user.id):
        await message.answer('🖍 Тут можна редагувати розклад', reply_markup=kb.schedule_in_exel(await rq.get_sheet_id_by_user_id(message.from_user.id)))
    else:
        await message.answer('🔎 Це може зробити тільки адмін')

@router.callback_query(F.data.startswith('update_all_schedule_'))
async def ask_yes_or_no(callback: CallbackQuery):
    result = callback.data.split('_')[-1]
    loading_symbols = ["⏳", "⌛️","⏳", "⌛️", "✅"]
    if result == 'yes':
        await callback.answer('🕒Це займе деякий час...')

        await callback.message.edit_text(f"Завантаження... ⏳")

        await rq.set_groups()
        await rq.clear_schedule()
        await rq.set_schedule()

        await callback.message.edit_text('Розклад успішно перезаписано ✅')

    else:
        await callback.message.edit_text('🔙Ви повернулися назад')
        await callback.answer('🔙Ви повернулися назад')


@router.callback_query(F.data.startswith('update_schedule_for_one_group_'))
async def ask_yes_or_no(callback: CallbackQuery):
    result = callback.data.split('_')[-1]
    #loading_symbols = ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕧", "🕖", "🕗", "🕘", "🕙", "🕚"]
    loading_symbols = ["⏳", "⌛️"]
    if result == 'yes':
        group_title = await rq.get_group_title_by_user_id(callback.from_user.id)
        await callback.answer('🕒Це займе деякий час...')

        await callback.message.edit_text(f"Завантаження... ⏳")

        await rq.set_groups()
        await rq.clear_all_subgroups_by_group(group_title)
        await rq.set_all_subgroups_by_group(group_title)

        await callback.message.edit_text(f'Розклад оновлено успішно для {group_title} ✅')

    else:
        await callback.message.edit_text('🔙Ви повернулися назад')
        await callback.answer('🔙Ви повернулися назад')


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
        await send_schedule(message, message.from_user.id, day, False, 1)

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
        await send_schedule(message, message.from_user.id, day, False, 2)

@router.callback_query(F.data.startswith('day_'))
async def schedule_for_day(callback: CallbackQuery):
    await callback.answer('')
    day = callback.data.split('_')[1]
    await send_schedule(callback, callback.from_user.id, day, True)
