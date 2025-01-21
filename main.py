import asyncio
import logging


from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
#from app.handlers import router
from app.database.models import async_main
from app.database.requests import add_admin, set_user, set_db
from app.utils import send_reminders
from app.keyboards.menu import set_bot_commands

from app.handlers import (
    commands_router,
    groups_router,
    menu_router,
    profile_router,
    schedule_router
)

from config import TOKEN

bot = Bot(token = TOKEN)

dp = Dispatcher()

scheduler = AsyncIOScheduler()

async def main():
    await set_db()

    dp.include_router(commands_router)
    dp.include_router(groups_router)
    dp.include_router(menu_router)
    dp.include_router(profile_router)
    dp.include_router(schedule_router)

    scheduler.add_job(send_reminders, "interval", minutes=1, args=[bot])
    scheduler.start()

    await set_bot_commands(bot)

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

"""
Для адмінів додати кнопку змінити розклад і додати силку на EXEL, та кнопку Оновити розклад

"""