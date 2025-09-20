from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.utils.scenario_loader import get_available_scenarios

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда начала работы с ботом"""
    welcome_text = (
        "👋 Добро пожаловать в бот для обучения!\n\n"
        "Доступные команды:\n"
        "/start_scenario - начать сценарий\n"
        "/scenarios - список доступных сценариев"
    )
    await message.answer(welcome_text)


@router.message(Command("scenarios"))
async def cmd_scenarios(message: Message):
    """Показать доступные сценарии"""
    scenarios = get_available_scenarios()

    if not scenarios:
        await message.answer("❌ Нет доступных сценариев")
        return

    text = "📚 Доступные сценарии:\n\n" + "\n".join(
        f"• {scenario}" for scenario in scenarios
    )

    await message.answer(text)