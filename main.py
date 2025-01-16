import asyncio
import logging


from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.handlers import router
from app.database.models import async_main
from app.database.requests import add_admin, set_user, set_groups
from app.utils import send_reminders
from app.keyboards.menu import set_bot_commands




from config import TOKEN

bot = Bot(token = TOKEN)

dp = Dispatcher()

scheduler = AsyncIOScheduler()

async def main():
    await async_main()
    await set_user(722714127)
    await add_admin(722714127)
    await set_groups()
    #await set_schedule()
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

"""
Для адмінів додати кнопку змінити розклад і додати силку на EXEL, та кнопку Оновити розклад

"""