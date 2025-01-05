import gspread
from sqlalchemy.util import await_fallback

from app.database.models import async_session
from app.database.models import User, Schedule, Group
from sqlalchemy import select



async def set_db() -> None:
    gc = gspread.service_account(filename='creds.json')
    spreadsheet = gc.open("Schedule")
    worksheets = spreadsheet.worksheets()

    for sheet in worksheets:
        title = sheet.title

        data = sheet.get_all_records()
        await add_group(title)
        group_id = await get_group_id_by_title(title)
        await set_schedule(data, group_id)

async def add_group(title: str):
    specialty, course, group, subgroup = title.split('-')[0], title.split('-')[1].split('/')[0][0], title.split('-')[1].split('/')[0][1], title.split('/')[1]

    async with async_session() as session:
        async with session.begin():
            group_exists = await session.scalar(
                select(Group).where(
                    Group.specialty == specialty,
                    Group.course == course,
                    Group.group == group,
                    Group.subgroup == subgroup
                )
            )

            if not group_exists:
                new_group = Group(
                    specialty=specialty,
                    course=course,
                    group=group,
                    subgroup=subgroup
                )
                session.add(new_group)
                await session.commit()
                print(f"Групу {title} успішно додано до таблиці Groups.")
            else:
                print(f"Група {title} вже існує в таблиці Groups.")


async def set_schedule(data: list[dict[str, int | float | str]], group_id: int):
    async with async_session() as session:
        async with session.begin():
            for record in data:
                schedule = Schedule(
                    group_id=group_id,
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

async def user_has_group(tg_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(User.group_id).where(User.tg_id == tg_id)
        )
        group_id = result.scalar()
        return group_id is not None

async def get_group_title_by_id(group_id: int) -> str:
    async with async_session() as session:
        result = await session.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar()

        if group:
            return f"{group.specialty}-{group.group}/{group.subgroup}"
        else:
            return "Групу не знайдено"

async def get_group_id_by_title(title: str) -> int:
    specialty, course, group, subgroup = title.split('-')[0], title.split('-')[1].split('/')[0][0], title.split('-')[1].split('/')[0][1], title.split('/')[1]

    async with async_session() as session:
        result = await session.scalar(
            select(Group.id).where(
                Group.specialty == specialty,
                Group.course == course,
                Group.group == group,
                Group.subgroup == subgroup
            )
        )
        return result

async def get_user_group_id_by_tg_id(tg_id: int) -> int:
    async with async_session() as session:
        result = await session.scalar(
            select(User.group_id).where(
                User.tg_id == tg_id
            )
        )
        return result

async def update_user_group(tg_id: int, group_title: str) -> None:
    group_id = await get_group_id_by_title(group_title)

    if group_id is None:
        print(f"Групу {group_title} не знайдено.")
        return

    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

            if user:
                user.group_id = group_id
                await session.commit()
                print(
                    f"Групу для користувача з tg_id={tg_id} успішно оновлено на group_id={group_id} для групи '{group_title}'.")
            else:
                print(f"Користувача з tg_id={tg_id} не знайдено.")


async def get_schedule_by_day(day: str, tg_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Schedule).where(
                Schedule.day == day,
                Schedule.group_id == await get_user_group_id_by_tg_id(tg_id)
            )
        )
        schedules = result.scalars().all()
        return schedules

async def get_all_specialties() -> list[str]:
    async with async_session() as session:
        result = await session.execute(select(Group.specialty).distinct())
        specialties = result.scalars().all()
        return specialties

async def get_all_courses(specialty: str) -> list[str]:
    async with async_session() as session:
        result = await session.execute(
            select(Group.course).where(Group.specialty == specialty).distinct()
        )
        courses = result.scalars().all()
        return courses

async def get_all_groups(specialty: str, course: str) -> list[str]:
    async with async_session() as session:
        result = await session.execute(
            select(Group.group).where(Group.specialty == specialty, Group.course == course).distinct()
        )
        groups = result.scalars().all()
        return groups

async def get_all_subgroups(specialty: str, course: str, group: str) -> list[str]:
    async with async_session() as session:
        result = await session.execute(
            select(Group.subgroup).where(Group.specialty == specialty, Group.course == course, Group.group == group).distinct()
        )
        subgroups = result.scalars().all()
        return subgroups