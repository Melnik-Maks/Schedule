from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import bold, italic

from aiogram import Bot
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner

from datetime import datetime, timedelta

from app.keyboards import yesterday_and_tomorrow

from app.database.requests import get_schedules_for_reminders, get_users_by_group_id, get_chats_by_group_id

def day_to_accusative(day: str) -> str:
    if day == 'Середа':
        return 'Середу'
    elif day == "П'ятниця":
        return "П'ятницю"
    elif day == "Субота":
        return 'Суботу'
    return day

def check_dates(dates: str, date: str) -> bool:
    periods = dates.split(',')
    for i in periods:
        if i.find('-') == -1:
            if i.lstrip().rsplit() == date:
                return True
        else:
            l, r = i.lstrip().rstrip().split('-')
            if date_comparison(l, date) and date_comparison(date, r):
                return True
    return False

def date_comparison(a: str, b: str) -> bool:
    d1, m1 = a.split('.')
    d2, m2 = b.split('.')
    if m1 != m2:
        return m1 < m2
    return d1 <= d2




async def send_schedule(destination: Message | CallbackQuery, day: str, schedule: list, add_buttons: bool, today = 0) -> None:
    message = destination.message if isinstance(destination, CallbackQuery) else destination

    schedule.sort(key=lambda x: int(x.time.split('-')[0].replace(':', '')))
    if today == 0:
        await message.answer(f"<b>💻 Розклад за {day_to_accusative(day)}:</b>", parse_mode="HTML")

    if not schedule:
        await message.answer_sticker("CAACAgIAAxUAAWd60zJyaJFXLJvhFaxCIq00nZ9DAALAUgACLiKgSoppqBV05QeNNgQ")
        if today == 1:
            await message.answer('На сьогодні немає пар :)')
        elif today == 2:
            await message.answer('На завтра немає пар :)')
        elif add_buttons:
            await message.answer('На цей день немає пар :)', reply_markup=await yesterday_and_tomorrow(day))
        else:
            await message.answer('На цей день немає пар :)')
    else:
        pair_count = 0
        for i in range(len(schedule)):
            subject_info = ''
            #subject_info += f"<b>❌На цей день цієї пари немає ❌</b>\n\n"
            if not(not add_buttons and not check_dates(schedule[i].weeks, message.date.now().strftime("%d.%m"))):
                pair_count += 1
                subject_info += (
                    f"📚 <b>{schedule[i].subject}</b>\n"
                    f"⏰ <i>{schedule[i].time}</i>\n"
                    f"📖 <i>{schedule[i].type.capitalize()}</i>\n"
                    f"👨‍🏫 {schedule[i].teacher}\n"
                )

                if schedule[i].room.strip():
                    subject_info += f"🏫 {schedule[i].room}\n"
                subject_info += f"🗓️ {schedule[i].weeks}\n"

                if schedule[i].zoom_link.strip():
                    subject_info += f"🔗 <a href='{schedule[i].zoom_link}'>Перейти до Zoom</a>\n"

                if add_buttons and i == len(schedule) - 1:
                    await message.answer(subject_info, parse_mode="HTML", reply_markup=await yesterday_and_tomorrow(day), disable_web_page_preview=True)
                else:
                    await message.answer(subject_info, parse_mode="HTML", disable_web_page_preview=True)
        if not pair_count:
            await message.answer_sticker("CAACAgIAAxUAAWd60zJyaJFXLJvhFaxCIq00nZ9DAALAUgACLiKgSoppqBV05QeNNgQ")
            if today == 1:
                await message.answer('На сьогодні немає пар :)')
            elif today == 2:
                await message.answer('На завтра немає пар :)')


async def send_reminders(bot):
    now = datetime.now()
    start_pair = now + timedelta(minutes=5)
    end_pair = now + timedelta(minutes=85)
    reminder_time = f'{start_pair.strftime("%H:%M")}-{end_pair.strftime("%H:%M")}'
    print(reminder_time)

    schedules = await get_schedules_for_reminders(reminder_time)

    for schedule in schedules:
        subject_info = f"⏰ <b>Нагадування про пару!</b>\n\n"
        subject_info += (
            f"📚 <b>{schedule.subject}</b>\n"
            f"⏰ <i>{schedule.time}</i>\n"
            f"📖 <i>{schedule.type.capitalize()}</i>\n"
            f"👨‍🏫 {schedule.teacher}\n"
        )

        if schedule.room.strip():
            subject_info += f"🏫 {schedule.room}\n"
        subject_info += f"🗓️ {schedule.weeks}\n"

        if schedule.zoom_link.strip():
            subject_info += f"🔗 <a href='{schedule.zoom_link}'>Перейти до Zoom</a>\n\n"
        subject_info += f"🚦<b>{schedule.type.capitalize()} почнеться через 5 хвилин!</b>"

        if schedule.type.strip().lower() == 'лекція':
            chats = await get_chats_by_group_id(schedule.group_id)
            for chat in chats:
                await bot.send_message(chat.chat_id, subject_info, parse_mode="HTML")

        users = await get_users_by_group_id(schedule.group_id)
        for user in users:
            await bot.send_message(user.tg_id, subject_info, parse_mode="HTML")

async def is_bot_admin(bot: Bot, chat_id: int) -> bool:
    member = await bot.get_chat_member(chat_id, bot.id)
    return member in [ChatMemberAdministrator, ChatMemberOwner]