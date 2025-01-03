from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import bold, italic

from app.keyboards import yesterday_and_tomorrow

async def send_schedule(destination: Message | CallbackQuery, day: str, schedule: list, add_buttons: bool) -> None:
    message = destination.message if isinstance(destination, CallbackQuery) else destination

    await message.answer(f"{bold('Розклад')} за {bold(day)}:\n", parse_mode="Markdown")

    if not schedule:
        await message.answer('На цей день немає пар :)')
    else:
        for i in range(len(schedule)):
            subject_info = (
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
