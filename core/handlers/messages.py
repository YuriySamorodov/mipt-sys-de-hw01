import asyncio
from aiogram import F, Router, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.database.models import async_session
from core.middlwares.db import DBMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from core.utils.yndx_gpt import YandexGPTManager
from core.handlers.logger import UserActionLogger

# Инициализация роутера, логгера и менеджера GPT
dialog_router = Router()
dialog_router.message.middleware(DBMiddleware(async_session))

manager = YandexGPTManager()
action_logger = UserActionLogger()


# Обработка только текстовых сообщений
@dialog_router.message(F.text)
async def handle_text_message(message: Message):
    chat_id = message.chat.id
    user_input = message.text

    response = await manager.send_message(chat_id, user_input)
    action_logger.log_action(message.from_user.id, 'answer')
    await message.answer(response)


# Fallback — для всех остальных типов сообщений
@dialog_router.message()
async def handle_non_text_message(message: Message):
    action_logger.log_action(message.from_user.id, 'answer')
    await message.answer("Я могу обработать только текст. Картинки обработаны не будут.")
