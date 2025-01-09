import asyncio
import logging


from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.handlers import router
from app.database.models import async_main
from app.database.requests import set_db
from app.utils import send_reminders
from app.keyboards.menu import set_bot_commands


from config import TOKEN

bot = Bot(token = TOKEN)

dp = Dispatcher()

scheduler = AsyncIOScheduler()

async def main():
    await async_main()
    #await set_db()
    dp.include_router(router)

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