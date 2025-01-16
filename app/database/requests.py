
from sqlalchemy.util import await_fallback

from app.database.models import async_session
from app.database.models import User, Schedule, Group, Chat
from sqlalchemy.sql import func
from sqlalchemy import select, delete
import gspread

async def set_groups() -> None:
    gc = gspread.service_account(filename='creds.json')
    spreadsheet = gc.open("Schedule")
    worksheets = spreadsheet.worksheets()

    for sheet in worksheets:
        await add_group(sheet.title, sheet.id)


async def set_schedule() -> None:
    gc = gspread.service_account(filename='creds.json')
    spreadsheet = gc.open("Schedule")
    worksheets = spreadsheet.worksheets()

    for sheet in worksheets:
        title = sheet.title
        data = sheet.get_all_records()
        group_id = await get_group_id_by_title(title)
        await set_schedule_for_group(data, group_id)



async def clear_all_subgroups_by_group(group: str):
    gc = gspread.service_account(filename='creds.json')
    spreadsheet = gc.open("Schedule")
    worksheets = spreadsheet.worksheets()

    for sheet in worksheets:
        if sheet.title[:-2] == group[:-2]:
            await clear_schedule_for_subgroup(await get_group_id_by_title(sheet.title))

async def set_all_subgroups_by_group(group: str):
    gc = gspread.service_account(filename='creds.json')
    spreadsheet = gc.open("Schedule")
    worksheets = spreadsheet.worksheets()

    subgroups = []
    for sheet in worksheets:
        if sheet.title[:-2] == group[:-2]:
            await set_schedule_for_group(sheet.get_all_records(), await get_group_id_by_title(sheet.title))
    return subgroups

async def clear_schedule_for_subgroup(group_id: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Schedule).where(Schedule.group_id == group_id))
        await session.commit()

async def clear_schedule():
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Schedule))
        await session.commit()

async def add_group(title: str, sheet_id: int):
    specialty, course, group, subgroup = title.split('-')[0], title.split('-')[1].split('/')[0][0], title.split('-')[1].split('/')[0][1], title.split('/')[1]

    async with async_session() as session:
        async with session.begin():
            group_exists = await session.scalar(
                select(Group).where(
                    Group.sheet_id == sheet_id,
                    Group.specialty == specialty,
                    Group.course == course,
                    Group.group == group,
                    Group.subgroup == subgroup
                )
            )

            if not group_exists:
                new_group = Group(
                    sheet_id=sheet_id,
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

async def add_admin(tg_id: int):
    async with async_session() as session:
        async with session.begin():
            admin = await session.scalar(
                select(User).where(
                    User.tg_id == tg_id
                )
            )

            if admin:
                if admin.is_admin:
                    print(f'Користувач {admin.tg_id} вже є адміном')
                else:
                    admin.is_admin = True
                    await session.commit()
                    print(f"Користувач {tg_id} успішно додано до адмінів.")
            else:
                print(f"Користувача {tg_id} немає")

async def is_admin(tg_id: int):
    async with async_session() as session:
        admin = await session.scalar(
            select(User).where(
                User.tg_id == tg_id
            )
        )

        if admin:
            return admin.is_admin
        return None

async def get_sheet_id_by_user_id(tg_id: int):
    async with async_session() as session:
        group = await get_group_by_user_id(tg_id)
        if group:
            return group.sheet_id
        else:
            return 0

async def set_chat(chat_id: int, specialty: str, course: str, group: str):
    async with async_session() as session:
        async with session.begin():
            chat = await get_chat_by_chat_id(chat_id)

            if not chat:
                new_chat = Chat(
                    chat_id=chat_id,
                    specialty=specialty,
                    course=course,
                    group=group
                )
                session.add(new_chat)
                await session.commit()
                print(f"Чат {chat_id} успішно додано до таблиці Chats.")
            else:
                print(f"Чат {chat_id} вже існує в таблиці Chats.")

async def get_chat_by_chat_id(chat_id):
    async with async_session() as session:
        chat = await session.scalar(select(Chat).where(Chat.chat_id == chat_id))
        return chat

async def update_chat_group(chat_id: int, specialty: str, course: str, group: str) -> None:
    async with async_session() as session:
        chat = await session.scalar(select(Chat).where(Chat.chat_id == chat_id))
        if chat:
            chat.specialty = specialty
            chat.course = course
            chat.group = group
            await session.commit()
            print(f"Для чату {chat_id} успішно оновлено групу {specialty}-{course}{group}")
        else:
            print(f"Чату з chat_id={chat_id} не знайдено.")


async def set_schedule_for_group(data: list[dict[str, int | float | str]], group_id: int):
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
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

            if not user:
                session.add(User(tg_id=tg_id, reminder=False, is_admin=False))
                await session.commit()

async def user_has_group(tg_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(User.group_id).where(User.tg_id == tg_id)
        )
        group_id = result.scalar()
        return group_id is not None

async def get_group_title_by_user_id(tg_id: int) -> str:
    async with async_session() as session:
        group_id = await get_user_group_id_by_tg_id(tg_id)
        result = await session.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar()

        if group:
            return f"{group.specialty}-{group.course}{group.group}/{group.subgroup}"
        else:
            return "Групу не знайдено"

async def get_group_title_by_id(group_id: int) -> str:
    async with async_session() as session:
        result = await session.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar()

        if group:
            return f"{group.specialty}-{group.course}{group.group}/{group.subgroup}"
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

async def get_user_reminder(tg_id: int) -> bool:
    async with async_session() as session:
        result = await session.scalar(
            select(User.reminder).where(
                User.tg_id == tg_id
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

async def set_user_group(tg_id: int, group_title: str) -> None:
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

async def turn_off_reminders(tg_id: int) -> None:
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

            if user:
                user.reminder = False
                await session.commit()
                print(
                    f"Для користувача з tg_id={tg_id} успішно вимкнено нагадування про пари.")
            else:
                print(f"Користувача з tg_id={tg_id} не знайдено.")

async def turn_on_reminders(tg_id: int) -> None:
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

            if user:
                user.reminder = True
                await session.commit()
                print(
                    f"Для користувача з tg_id={tg_id} успішно увімкнено нагадування про пари.")
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



async def get_users_by_group_id(group_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.group_id == group_id,
                User.reminder == True,
            )
        )
        users = result.scalars().all()
        return users

async def get_group_by_user_id(tg_id: int):
    async with async_session() as session:
        group_id = await get_user_group_id_by_tg_id(tg_id)
        if group_id:
            group = await session.scalar(select(Group).where(Group.id == group_id))
            return group
        return None


async def get_group_by_group_id(group_id: int):
    async with async_session() as session:
        group = await session.scalar(select(Group).where(Group.id == group_id))
        return group

async def get_user_by_user_id(user_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        return user

async def get_chats_by_group_id(group_id: int):
    async with async_session() as session:

        group = await get_group_by_group_id(group_id)

        result = await session.execute(
            select(Chat).where(
                Chat.specialty == group.specialty,
                Chat.course == group.course,
                Chat.group == group.group
            )
        )
        chats = result.scalars().all()
        return chats

async def get_schedules_for_reminders(reminder_time: str):
    async with async_session() as session:
        result = await session.execute(
            select(Schedule).where(
                Schedule.time == reminder_time
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