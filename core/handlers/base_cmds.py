from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.types.webhook_info import WebhookInfo
from aiogram.fsm.context import FSMContext
from core.FSM.dialog_FSM import DialogReg
# import core.keyboards.reply_kb as reply_kb
# import core.keyboards.inline_kb as inline_kb
from core.database.models import async_session
from core.middlwares.db import DBMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.requests import add_user_stat
from core.handlers.logger import UserActionLogger

action_logger = UserActionLogger()
base_cmd_router = Router()
base_cmd_router.message.middleware(DBMiddleware(async_session))

@base_cmd_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    await state.set_state(DialogReg.start)

    action_logger.log_action(message.from_user.id, 'start')


    user_name = message.from_user.first_name or "дорогой друг"

    
    await add_user_stat(session,
                        message.from_user.id,
                        message.date,
                        'start')

    await message.answer("Привет, {user_name}! Задайте мне вопрос, и я отвечу")


@base_cmd_router.message(Command('help'))
async def get_help(message: Message):
    with open('Руководство пользователя.txt', 'rb') as file:
        await message.answer_document(FSInputFile("Руководство пользователя.txt"), caption="Руководство пользователя")


