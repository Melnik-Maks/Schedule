import gspread

from app.database.models import async_session
from app.database.models import User, Schedule
from sqlalchemy import select

async def set_db():
    gc = gspread.service_account(filename='creds.json')
    worksheet = gc.open("КН-22/1").sheet1
    list_of_dicts = worksheet.get_all_records()
    await set_schedule(list_of_dicts)

async def set_schedule(data: list[dict[str, int | float | str]]):
    async with async_session() as session:
        async with session.begin():
            for record in data:
                schedule = Schedule(
                    day=record["День"],
                    time=record["Час"],
                    subject=record["Предмет"],
                    type=record["Тип заняття"],
                    teacher=record["Викладач"],
                    room=record["Аудиторія"],
                    zoom_link=record["Посилання (онлайн)"],
                    weeks=record["Тижні"]
                )
                session.add(schedule)
        await session.commit()


async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def get_schedule_by_day(day: str):
    async with async_session() as session:
        result = await session.execute(select(Schedule).where(Schedule.day == day))
        schedules = result.scalars().all()
        return schedules

