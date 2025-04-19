from core.database.models import async_session
from sqlalchemy import select, delete, update, func
from sqlalchemy.dialects.postgresql import TEXT
import asyncio
from core.database.models import UserStat
import json
import pandas as pd
import os

import datetime

async def add_user_stat(session, user_tg_id: int, datetime: datetime.datetime, action: str) -> None:
    new_stat = UserStat(user_tg_id=user_tg_id, datetime=datetime, action=action)
    session.add(new_stat)
    await session.commit()