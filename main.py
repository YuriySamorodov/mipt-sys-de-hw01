import asyncio
import os
from dotenv import load_dotenv, set_key
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.fsm.context import FSMContext, StorageKey
from aiogram.exceptions import TelegramForbiddenError

from core.handlers.base_cmds import base_cmd_router
from core.handlers.messages import dialog_router
from core.callbacks.yndx_score import clbs_router
from core.database.models import async_main
from core.handlers.logger import UserActionLogger

# Инициализация логгера
action_logger = UserActionLogger()

async def run_bot():
    """Основная функция для запуска бота"""
    # Загрузка переменных окружения
    load_dotenv()
    
    # Инициализация базы данных
    await async_main()

    # Создание экземпляра бота
    bot = Bot(token=os.getenv('BOTTOKEN'))

    # Удаление вебхука для обработки обновлений через polling
    await bot(DeleteWebhook(drop_pending_updates=True))

    # Создание диспетчера и подключение роутеров
    dp = Dispatcher()
    dp.include_routers(
        base_cmd_router,
        dialog_router,
        clbs_router
    )

    # Логирование старта бота
    print("Бот запущен и готов к работе...")
    
    # Запуск обработки входящих сообщений
    await dp.start_polling(bot)

async def main():
    """Точка входа для асинхронного запуска"""
    await asyncio.gather(run_bot())

if __name__ == "__main__":
    # Запуск бота с обработкой асинхронных операций
    asyncio.run(main())
