from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import bold, italic
from typing import Union

from aiogram import Bot
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner
from aiogram.exceptions import TelegramForbiddenError

from datetime import datetime, timedelta

from app.keyboards import yesterday_and_tomorrow

from app.database.requests import get_schedules_for_reminders, get_users_for_reminder_by_group_id, get_chats_by_group_id, get_schedule_by_day, get_group_title_by_id
from config import daysOfTheWeek
import pytz


def day_to_accusative(day: str) -> str:
    if day == 'Середа':
        return 'Середу'
    elif day == "П'ятниця":
        return "П'ятницю"
    elif day == "Субота":
        return 'Суботу'
    return day

def check_dates(dates: str, alternation: bool, today: int) -> bool:
    if not dates.strip():
        return True
    timezone = pytz.timezone('Europe/Kyiv')
    date = datetime.now(timezone)
    if today == 2:
        date += timedelta(days=1)

    periods = dates.split(',')
    for i in periods:
        if i.find('-') == -1:
            if i.lstrip().rsplit() == date:
                return True
        else:
            l, r = i.lstrip().rstrip().split('-')
            if date_comparison(l, date.strftime("%d.%m")) and date_comparison(date.strftime("%d.%m"), r):
                if alternation:
                    date2 = datetime.strptime(f"{date.year}.{l}", "%Y.%d.%m")
                    if date.strftime('%d.%m') == date2.strftime('%d.%m'):
                        return True
                    difference = (date - date2).days
                    return difference % 14 == 0
                return True
    return False

def check_alternation(date2: str):
    timezone = pytz.timezone('Europe/Kyiv')
    date = datetime.now(timezone)
    date2 = datetime.strptime(f"{date.year}.{date2}", "%y.%d.%m")

    difference = (date - date2).days
    return difference % 14 == 0

def date_comparison(a: str, b: str) -> bool:
    d1, m1 = a.split('.')
    d2, m2 = b.split('.')
    if int(m1) != int(m2):
        return int(m1) < int(m2)
    return int(d1) <= int(d2)




async def send_schedule(destination: Union[Message, CallbackQuery], tg_id: int, day: str, add_buttons: bool, today: int = 0) -> None:
    message = destination.message if isinstance(destination, CallbackQuery) else destination
    schedule = await get_schedule_by_day(day, tg_id)

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
            subject_info = (
                f"📚 <b>{schedule[i].subject}</b>\n"
                f"⏰ <i>{schedule[i].time}</i>\n"
                f"📖 <i>{schedule[i].type.capitalize()}</i>\n"
                f"👨‍🏫 {schedule[i].teacher}\n"
            )

            if schedule[i].room.strip():
                subject_info += f"🏫 {schedule[i].room}\n"
            subject_info += f"🗓️ {schedule[i].weeks}"

            if schedule[i].alternation:
                subject_info += f" <b>ч/т</b>"
            subject_info += "\n"

            if schedule[i].zoom_link.strip():
                subject_info += f"🔗 <a href='{schedule[i].zoom_link}'>Перейти до Zoom</a>\n"

            if add_buttons and i == len(schedule) - 1:
                await message.answer(subject_info, parse_mode="HTML", reply_markup=await yesterday_and_tomorrow(day),
                                     disable_web_page_preview=True)
            elif add_buttons:
                await message.answer(subject_info, parse_mode="HTML", disable_web_page_preview=True)
            elif check_dates(schedule[i].weeks, schedule[i].alternation, today = today):
                pair_count += 1
                await message.answer(subject_info, parse_mode="HTML", disable_web_page_preview=True)

        if not add_buttons and not pair_count:
            await message.answer_sticker("CAACAgIAAxUAAWd60zJyaJFXLJvhFaxCIq00nZ9DAALAUgACLiKgSoppqBV05QeNNgQ")
            if today == 1:
                await message.answer('На сьогодні немає пар :)')
            elif today == 2:
                await message.answer('На завтра немає пар :)')


async def send_reminders(bot):
    timezone = pytz.timezone('Europe/Kyiv')
    now = datetime.now(timezone)
    if now.weekday() == 6:
        return
    start_pair = now + timedelta(minutes=5)
    end_pair = now + timedelta(minutes=85)
    reminder_time = f'{start_pair.strftime("%H:%M")}-{end_pair.strftime("%H:%M")}'

    day = daysOfTheWeek[now.weekday()]
    schedules = await get_schedules_for_reminders(day, reminder_time)

    for schedule in schedules:
        if check_dates(schedule.weeks, schedule.alternation, today=0):
            #subject_info = f"⏰ <b>Нагадування про пару!</b>\n\n"
            subject_info = (
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

            chats = await get_chats_by_group_id(schedule.group_id)
            for chat in chats:
                try:
                    await bot.send_message(chat.chat_id, f"🚨🚨🚨\n⏰ <b>Нагадування про пару для <strong>{await get_group_title_by_id(schedule.group_id)}/{schedule.subgroup}</strong>!</b>\n\n" + subject_info, parse_mode="HTML", disable_web_page_preview=True)
                except TelegramForbiddenError:
                    print("Бота було видалено з групового чату.")

            users = await get_users_for_reminder_by_group_id(schedule.group_id, schedule.subgroup)
            for user in users:
                await bot.send_message(user.tg_id, f"⏰ <b>Нагадування про пару!</b>\n\n" + subject_info, parse_mode="HTML", disable_web_page_preview=True)

async def is_bot_admin(bot: Bot, chat_id: int) -> bool:
    member = await bot.get_chat_member(chat_id, bot.id)
    return member in [ChatMemberAdministrator, ChatMemberOwner]