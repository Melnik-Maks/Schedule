from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import bold, italic

async def send_schedule(destination: Message | CallbackQuery, day: str, schedule: list) -> None:
    message = destination.message if isinstance(destination, CallbackQuery) else destination

    await message.answer(f"{bold('Розклад')} за {bold(day)}:\n", parse_mode="Markdown")

    if not schedule:
        await message.answer('На цей день немає пар :)')
    else:
        for i in schedule:
            subject_info = (
                f"{bold('Предмет:')} {i.subject}\n"
                f"{bold('Час:')} {i.time}\n"
                f"{bold('Тип заняття:')} {italic(i.type)}\n"
                f"{bold('Викладач:')} {i.teacher}\n"
                f"{bold('Аудиторія:')} {i.room}\n"
                f"{bold('Тижні:')} {i.weeks}\n"
            )

            if i.type.lower() == 'лекція':
                subject_info += f"{bold('Zoom:')} {i.zoom_link}\n"

            await message.answer(subject_info, parse_mode="Markdown")