import asyncio
import logging
from aiogram import Bot, Dispatcher

from bot.config import BOT_TOKEN
from bot.handlers.start_handler import router as start_router
from bot.handlers.scenario_handler import router as scenario_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(start_router)
    dp.include_router(scenario_router)

    # Запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())