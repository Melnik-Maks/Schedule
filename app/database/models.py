from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'), nullable=True)
    subgroup: Mapped[int] = mapped_column(nullable=True)
    reminder: Mapped[bool] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(nullable=False)
    sticker_id: Mapped[str] = mapped_column(nullable=False)


class Schedule(Base):
    __tablename__ = 'schedule'

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'))
    subgroup: Mapped[int] =  mapped_column(nullable=False)
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    time: Mapped[str] = mapped_column(String(20), nullable=False)
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50))
    teacher: Mapped[str] = mapped_column(String(100))
    room: Mapped[str] = mapped_column(String(20))
    zoom_link: Mapped[str] = mapped_column(String(255))
    weeks: Mapped[str] = mapped_column(String(100))
    alternation: Mapped[bool] = mapped_column()


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    sheet_id: Mapped[int] = mapped_column(nullable=False)
    specialty: Mapped[str] = mapped_column(String(20), nullable=False)
    course: Mapped[str] = mapped_column(String(20), nullable=False)
    group: Mapped[str] = mapped_column(String(20), nullable=False)
    subgroups: Mapped[str] = mapped_column(nullable=False)

class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'))

    #specialty: Mapped[str] = mapped_column(String(20), nullable=False)
    #course: Mapped[str] = mapped_column(String(20), nullable=False)
    #group: Mapped[str] = mapped_column(String(20), nullable=False)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)