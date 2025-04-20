import asyncio
import time

from core.FSM.dialog_FSM import DialogReg
from aiogram import F, Router, types
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from core.database.models import async_session
from core.middlwares.db import DBMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import re
from core.utils.yndx_gpt import YandexGPTManager
from core.handlers.logger import UserActionLogger


action_logger = UserActionLogger()
dialog_router = Router()
dialog_router.message.middleware(DBMiddleware(async_session))
manager = YandexGPTManager()


@dialog_router.message()
async def handle_message(message: Message):
    chat_id = message.chat.id
    response = await manager.send_message(chat_id, message.text)
    action_logger.log_action(message.from_user.id, 'answer')
    await message.answer(response)
