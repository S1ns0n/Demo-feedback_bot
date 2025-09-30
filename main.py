import asyncio
import logging
from aiogram import Bot, Dispatcher

from bot.config import BOT_TOKEN, ROOT_DIR
from bot.handlers.start_handler import router as start_router
from bot.handlers.scenario_handler import router as scenario_router
from bot.handlers.admin_handler import router as admin_router
from bot.middlewares import exist_middleware
# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()


    dp.update.outer_middleware(exist_middleware)

    # Регистрация роутеров
    dp.include_router(start_router)
    dp.include_router(scenario_router)
    dp.include_router(admin_router)

    # Запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    print(ROOT_DIR)
    asyncio.run(main())