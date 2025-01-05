from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import bold, italic

from app.keyboards import yesterday_and_tomorrow

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


async def send_schedule(destination: Message | CallbackQuery, day: str, schedule: list, add_buttons: bool) -> None:
    message = destination.message if isinstance(destination, CallbackQuery) else destination

    await message.answer(f"<b>💻 Розклад за {day_to_accusative(day)}:</b>", parse_mode="HTML")

    if not schedule:
        await message.answer('На цей день немає пар :)')
    else:
        for i in range(len(schedule)):
            subject_info = ''

            if add_buttons and not check_dates(schedule[i].weeks, message.date.now().strftime("%d.%m")):
                subject_info += f"<b>❌❌❌На цей день цієї пари немає ❌❌❌</b>\n\n"

            subject_info += (
                f"📚 <b>{schedule[i].subject}</b>\n"
                f"⏰ <i>{schedule[i].time}</i>\n"
                f"📖 <i>{schedule[i].type.capitalize()}</i>\n"
                f"👨‍🏫 {schedule[i].teacher}\n"
                f"🏫 {schedule[i].room}\n"
                f"🗓️ {schedule[i].weeks}\n"
            )

            if schedule[i].type.lower() == 'лекція':
                subject_info += f"🔗 <a href='{schedule[i].zoom_link}'>{schedule[i].zoom_link}</a>\n"

            if add_buttons and i == len(schedule) - 1:
                await message.answer(subject_info, parse_mode="HTML", reply_markup=await yesterday_and_tomorrow(day))
            else:
                await message.answer(subject_info, parse_mode="HTML")
