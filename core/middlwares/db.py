from typing import Any, Dict
from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import async_session
from aiogram.types import TelegramObject

class DBMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_session):
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        hanlder,
        event: TelegramObject,
        data: Dict[str, Any]
    ):
        async with self.sessionmaker() as session:
            data['session'] = session
            return await hanlder(event, data)
