import gspread

from app.database.models import async_session
from app.database.models import User, Schedule
from sqlalchemy import select

async def set_db() -> None:
    gc = gspread.service_account(filename='creds.json')
    spreadsheet = gc.open("Schedule")
    worksheets = spreadsheet.worksheets()

    for sheet in worksheets:
        title = sheet.title

        data = sheet.get_all_records()
        await set_schedule(data, title)

async def set_schedule(data: list[dict[str, int | float | str]], title: str):
    async with async_session() as session:
        async with session.begin():
            group = title.split('/')[0]
            subgroup = title.split('/')[1]
            for record in data:
                schedule = Schedule(
                    day=record["День"],
                    group=group,
                    subgroup=subgroup,
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

async def get_schedule_by_day(request : str):
    async with async_session() as session:
        day, group, subgroup = request.split('/')
        result = await session.execute(
            select(Schedule).where(
                Schedule.day == day,
                Schedule.group == group,
                Schedule.subgroup == subgroup
            )
        )
        schedules = result.scalars().all()
        return schedules

async def get_all_groups() -> list[str]:
    async with async_session() as session:
        result = await session.execute(select(Schedule.group).distinct())
        groups = result.scalars().all()
        return groups

async def get_all_subgroups_by_group(group: str) -> list[str]:
    async with async_session() as session:
        result = await session.execute(
            select(Schedule.subgroup).filter(Schedule.group == group).distinct()
        )
        subgroups = result.scalars().all()

        return subgroups