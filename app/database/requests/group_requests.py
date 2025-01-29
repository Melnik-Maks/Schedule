from app.database.models import async_session
from app.database.models import User, Schedule, Group, Chat
from sqlalchemy.sql import func
from typing import List, Dict, Union
from sqlalchemy import select, delete
import gspread

from typing import List


from gspread.exceptions import APIError

async def set_groups() -> None:
    try:
        gc = gspread.service_account(filename="creds.json")
        spreadsheet = gc.open("Schedule")
        worksheets = spreadsheet.worksheets()

        for sheet in worksheets:
            try:
                group = await get_group_by_title(sheet.title)
                if not group:
                    subgroups = sheet.col_values(1)[1:]
                    unique_subgroups = set()
                    for subgroup in subgroups:
                        parts = subgroup.strip().replace(' ', '').split(',')
                        unique_subgroups.update(part for part in parts)
                    list_subgroups = sorted(list(unique_subgroups))
                    await add_group(sheet.title, ','.join(list_subgroups), sheet.id)
            except Exception as e:
                print(f"Помилка обробки листа '{sheet.title}': {e}")
    except FileNotFoundError:
        print("Файл 'creds.json' не знайдено.")
    except APIError as api_err:
        print(f"Помилка API Google Sheets: {api_err}")
    except Exception as e:
        print(f"Несподівана помилка в set_groups: {e}")

async def set_all_subgroups_by_group(group: str):
    from .schedule_requests import set_schedule_for_group
    try:
        gc = gspread.service_account(filename="creds.json")
        spreadsheet = gc.open("Schedule")
        worksheets = spreadsheet.worksheets()

        for sheet in worksheets:
            if sheet.title == group:
                try:
                    await set_schedule_for_group(sheet.get_all_records(), await get_group_id_by_title(sheet.title))
                except Exception as e:
                    print(f"Помилка встановлення підгруп для групи '{group}': {e}")
    except FileNotFoundError:
        print("Файл 'creds.json' не знайдено.")
    except APIError as api_err:
        print(f"Помилка API Google Sheets: {api_err}")
    except Exception as e:
        print(f"Несподівана помилка в set_all_subgroups_by_group: {e}")

async def add_group(title: str, subgroups: str, sheet_id: int):
    specialty, course, group = title.split('-')[0], title.split('-')[1][0], title.split('-')[1][1]
    async with async_session() as session:
        async with session.begin():
            group_exists = await session.scalar(
                select(Group).where(
                    Group.sheet_id == sheet_id,
                    Group.specialty == specialty,
                    Group.course == course,
                    Group.group == group,
                )
            )

            if not group_exists:
                new_group = Group(
                    sheet_id=sheet_id,
                    specialty=specialty,
                    course=course,
                    group=group,
                    subgroups=subgroups,
                )
                session.add(new_group)
                await session.commit()
                print(f"Групу {title} успішно додано до таблиці Groups.")
            else:
                print(f"Група {title} вже існує в таблиці Groups.")

async def get_sheet_id_by_user_id(tg_id: int):
    async with async_session() as session:
        group = await get_group_by_user_id(tg_id)
        if group:
            return group.sheet_id
        else:
            return 0

async def get_group_title_by_user_id(tg_id: int) -> str:
    from .user_requests import get_user_group_id_by_tg_id
    async with async_session() as session:
        group_id = await get_user_group_id_by_tg_id(tg_id)
        result = await session.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar()

        if group:
            return f"{group.specialty}-{group.course}{group.group}"
        else:
            return "Групу не знайдено"

async def get_group_title_by_id(group_id: int) -> str:
    async with async_session() as session:
        result = await session.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar()

        if group:
            return f"{group.specialty}-{group.course}{group.group}"
        else:
            return "None"

async def get_group_by_title(title: str) -> int:
    specialty, course, group = title.split('-')[0], title.split('-')[1][0], title.split('-')[1][1],
    async with async_session() as session:
        result = await session.scalar(
            select(Group).where(
                Group.specialty == specialty,
                Group.course == course,
                Group.group == group,
            )
        )
        return result

async def get_group_id_by_title(title: str) -> int:
    specialty, course, group = title.split('-')[0], title.split('-')[1][0], title.split('-')[1][1],
    async with async_session() as session:
        result = await session.scalar(
            select(Group.id).where(
                Group.specialty == specialty,
                Group.course == course,
                Group.group == group,
            )
        )
        return result

async def get_group_id_by_group(specialty: str, course: str, group: str) -> int:
    async with async_session() as session:
        result = await session.scalar(
            select(Group.id).where(
                Group.specialty == specialty,
                Group.course == course,
                Group.group == group,
            )
        )
        return result

async def get_group_by_user_id(tg_id: int):
    from .user_requests import get_user_group_id_by_tg_id
    async with async_session() as session:
        group_id = await get_user_group_id_by_tg_id(tg_id)
        if group_id:
            group = await session.scalar(select(Group).where(Group.id == group_id))
            return group
        return None


async def get_groups():
    async with async_session() as session:
        result = await session.execute(
            select(Group)
        )
        groups = result.scalars().all()
        return groups


async def get_group_by_group_id(group_id: int):
    async with async_session() as session:
        group = await session.scalar(select(Group).where(Group.id == group_id))
        return group

async def get_all_specialties() -> List[str]:
    async with async_session() as session:
        result = await session.execute(select(Group.specialty).distinct())
        specialties = result.scalars().all()
        return specialties

async def get_all_courses(specialty: str) -> List[str]:
    async with async_session() as session:
        result = await session.execute(
            select(Group.course).where(Group.specialty == specialty).distinct()
        )
        courses = result.scalars().all()
        return courses

async def get_all_groups(specialty: str, course: str) -> List[str]:
    async with async_session() as session:
        result = await session.execute(
            select(Group.group).where(Group.specialty == specialty, Group.course == course).distinct()
        )
        groups = result.scalars().all()
        return groups

async def get_all_subgroups(specialty: str, course: str, group: str) -> List[str]:
    async with async_session() as session:
        subgroups = await session.scalar(
            select(Group.subgroups).where(Group.specialty == specialty, Group.course == course, Group.group == group)
        )
        return subgroups.split(',')