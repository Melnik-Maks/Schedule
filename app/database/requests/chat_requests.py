from app.database.models import async_session
from app.database.models import User, Schedule, Group, Chat
from sqlalchemy.sql import func
from typing import List, Dict, Union
from sqlalchemy import select, delete
import gspread


async def set_chat(chat_id: int, group_id: int):
    async with async_session() as session:
        async with session.begin():
            chat = await get_chat_by_chat_id(chat_id)

            if not chat:
                new_chat = Chat(
                    chat_id=chat_id,
                    group_id=group_id,
                )
                session.add(new_chat)
                await session.commit()
                print(f"Чат {chat_id} успішно додано до таблиці Chats.")
            else:
                print(f"Чат {chat_id} вже існує в таблиці Chats.")


async def get_chat_by_chat_id(chat_id: int):
    async with async_session() as session:
        chat = await session.scalar(select(Chat).where(Chat.chat_id == chat_id))
        return chat

async def update_chat_group(chat_id: int, group_id: int) -> None:
    from .group_requests import get_group_title_by_id
    async with async_session() as session:
        chat = await session.scalar(select(Chat).where(Chat.chat_id == chat_id))
        if chat:
            chat.group_id = group_id
            await session.commit()
            print(f"Для чату {chat_id} успішно оновлено групу {await get_group_title_by_id(group_id)}")
        else:
            print(f"Чату з chat_id={chat_id} не знайдено.")

async def get_chats_by_group_id(group_id: int):
    async with async_session() as session:

        result = await session.execute(
            select(Chat).where(
                Chat.group_id == group_id,

            )
        )
        chats = result.scalars().all()
        return chats
