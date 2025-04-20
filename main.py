import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook

from core.handlers.base_cmds import base_cmd_router
from core.handlers.messages import dialog_router
from core.callbacks.yndx_score import clbs_router
from core.database.models import async_main
from core.handlers.logger import UserActionLogger

# Инициализация логгера
action_logger = UserActionLogger()

async def run_bot():
    """Основная функция для запуска бота"""
    load_dotenv()
    await async_main()

    bot = Bot(token=os.getenv('BOTTOKEN'))
    await bot(DeleteWebhook(drop_pending_updates=True))

    dp = Dispatcher()
    dp.include_routers(
        base_cmd_router,
        dialog_router,
        clbs_router
    )

    await dp.start_polling(bot)

async def main():
    """Точка входа для асинхронного запуска"""
    await asyncio.gather(run_bot())

if __name__ == "__main__":
    asyncio.run(main())
