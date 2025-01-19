from app.database.models import async_session
from app.database.models import User, Schedule, Group, Chat
from sqlalchemy.sql import func
from typing import List, Dict, Union
from sqlalchemy import select, delete
import gspread

from gspread.exceptions import APIError

async def set_schedule() -> None:
    from .group_requests import get_group_id_by_title
    try:
        gc = gspread.service_account(filename="creds.json")
        spreadsheet = gc.open("Schedule")
        worksheets = spreadsheet.worksheets()

        for sheet in worksheets:
            try:
                title = sheet.title
                data = sheet.get_all_records()
                group_id = await get_group_id_by_title(title)
                await set_schedule_for_group(data, group_id)
            except Exception as e:
                print(f"Помилка обробки розкладу для листа '{sheet.title}': {e}")
    except FileNotFoundError:
        print("Файл 'creds.json' не знайдено.")
    except APIError as api_err:
        print(f"Помилка API Google Sheets: {api_err}")
    except Exception as e:
        print(f"Несподівана помилка в set_schedule: {e}")

async def clear_all_subgroups_by_group(group: str):
    from .group_requests import get_group_id_by_title
    try:
        gc = gspread.service_account(filename="creds.json")
        spreadsheet = gc.open("Schedule")
        worksheets = spreadsheet.worksheets()

        for sheet in worksheets:
            if sheet.title == group:
                try:
                    await clear_schedule_for_group(await get_group_id_by_title(sheet.title))
                except Exception as e:
                    print(f"Помилка очищення підгруп для групи '{group}': {e}")
    except FileNotFoundError:
        print("Файл 'creds.json' не знайдено.")
    except APIError as api_err:
        print(f"Помилка API Google Sheets: {api_err}")
    except Exception as e:
        print(f"Несподівана помилка в clear_all_subgroups_by_group: {e}")

async def clear_schedule_for_group(group_id: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Schedule).where(Schedule.group_id == group_id))
        await session.commit()

async def clear_schedule():
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Schedule))
        await session.commit()

async def set_schedule_for_group(data: List[Dict[str, Union[int, float, str]]], group_id: int):
    async with async_session() as session:
        async with session.begin():
            for record in data:
                for subgroup in str(record["Підгрупи"]).strip().replace(' ', '').split(','):
                    schedule = Schedule(
                        group_id=group_id,
                        subgroup=subgroup,
                        day=record["День"].capitalize(),
                        time=record["Час"],
                        subject=record["Предмет"],
                        type=record["Тип заняття"],
                        teacher=record["Викладач"],
                        room=str(record["Аудиторія"]),
                        zoom_link=record["Посилання"],
                        weeks=record["Тижні"]
                    )
                    session.add(schedule)
        await session.commit()

async def get_schedule_by_day(day: str, tg_id: int):
    from .user_requests import get_user_group_id_by_tg_id, get_user_subgroup_by_user_id
    async with async_session() as session:
        user_group_id = await get_user_group_id_by_tg_id(tg_id)
        user_subgroup = await get_user_subgroup_by_user_id(tg_id)

        result = await session.execute(
            select(Schedule).where(
                Schedule.day == day.capitalize(),
                Schedule.group_id == user_group_id,
                Schedule.subgroup == user_subgroup,
            )
        )
        schedules = result.scalars().all()
        return schedules

async def get_schedules_for_reminders(reminder_time: str):
    async with async_session() as session:
        result = await session.execute(
            select(Schedule).where(
                Schedule.time == reminder_time
            )
        )
        schedules = result.scalars().all()
        return schedules

