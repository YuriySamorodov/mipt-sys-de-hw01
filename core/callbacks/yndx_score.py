import core.keyboards.reply_kb as reply_kb
from core.FSM.dialog_FSM import DialogReg
from aiogram.fsm.context import FSMContext
import core.keyboards.inline_kb as inline_kb
from core.middlwares.db import DBMiddleware

from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import async_session
from aiogram import F, Router
from aiogram import CallbackQuery
import re
import os
import json
import ast
from dotenv import load_dotenv, set_key, get_key, dotenv_values
import dotenv
from aiogram.types import InputMediaPhoto, InputMediaVideo
import asyncio
from core.handlers.logger import UserActionLogger

action_logger = UserActionLogger()
clbs_router = Router()
clbs_router.callback_query.middleware(DBMiddleware(async_session))

# сюда позже добавим обработки клавиатуры для оценки ответов бота

@clbs_router.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    """Обработчик callback-запросов"""
    action_logger.log_action(callback.from_user.id, 'callback')
    await callback.answer() 
