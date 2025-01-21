from app.database.models import async_session
from app.database.models import User, Schedule, Group, Chat
from sqlalchemy.sql import func
from typing import List, Dict, Union
from sqlalchemy import select, delete
import gspread


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

async def delete_admin(tg_id: int):
    async with async_session() as session:
        async with session.begin():
            admin = await session.scalar(
                select(User).where(
                    User.tg_id == tg_id
                )
            )

            if admin:
                if not admin.is_admin:
                    print(f'Користувач {admin.tg_id} НЕ є адміном')
                else:
                    admin.is_admin = False
                    await session.commit()
                    print(f"Користувач {tg_id} успішно видалено з адмінів.")
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

async def get_all_admins():
    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.is_admin == True,
            )
        )
        users = result.scalars().all()
        return users

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
    from .group_requests import get_group_id_by_title
    group_id = await get_group_id_by_title(group_title.split('/')[0])

    if group_id is None:
        print(f"Групу {group_title} не знайдено.")
        return

    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

            if user:
                user.group_id = group_id
                user.subgroup = int(group_title.split('/')[1])
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
                print(f"Для користувача з tg_id={tg_id} успішно вимкнено нагадування про пари.")
            else:
                print(f"Користувача з tg_id={tg_id} не знайдено.")

async def turn_on_reminders(tg_id: int) -> None:
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

            if user:
                user.reminder = True
                await session.commit()
                print(f"Для користувача з tg_id={tg_id} успішно увімкнено нагадування про пари.")
            else:
                print(f"Користувача з tg_id={tg_id} не знайдено.")

async def get_user_subgroup_by_user_id(tg_id: int) -> int:
    async with async_session() as session:
        subgroup = await session.scalar(
            select(User.subgroup).where(User.tg_id == tg_id)
        )
        return subgroup


async def get_users_for_reminder_by_group_id(group_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.group_id == group_id,
                User.reminder == True,
            )
        )
        users = result.scalars().all()
        return users

async def get_user_by_user_id(user_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        return user

