from .chat_requests import *
from .group_requests import *
from .schedule_requests import *
from .user_requests import *

from app.database.models import async_main

async def set_db():
    await async_main()
    await set_user(722714127)
    await add_admin(722714127)
    await set_groups()
    await clear_schedule()
    await set_schedule()
