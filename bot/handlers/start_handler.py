from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.menu_keyboards import create_menu_scenarios_list_keyboard
from bot.utils.scenario_loader import get_available_scenarios
from bot.utils.scenario_loader import load_scenario
from bot.handlers.scenario_handler import send_scenario_step
from bot.states.user_state import UserState
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда начала работы с ботом"""
    welcome_text = (
        "👋 Добро пожаловать в бот для обучения!\n\n"
        "Доступные команды:\n"
        "/scenarios - список доступных сценариев"
    )
    await message.answer(welcome_text)


@router.message(Command("scenarios"))
async def cmd_start_scenario(message: Message):
    """Выбор сценария из списка"""
    keyboard = create_menu_scenarios_list_keyboard()
    await message.answer("🎯 Выберите сценарий для запуска:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("start_scenario_"))
async def handle_scenario_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора сценария"""
    scenario_name = callback.data.replace("start_scenario_", "")


    scenario = load_scenario(scenario_name)

    if not scenario:
        await callback.answer("❌ Сценарий не найден или поврежден", show_alert=True)
        return

    # Запускаем выбранный сценарий
    await state.set_state(UserState.in_scenario)
    await state.update_data(
        scenario=scenario,
        current_step=0
    )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"🚀 Запускаем сценарий: {scenario['name']}")


    await send_scenario_step(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "refresh_scenarios")
async def handle_refresh_scenarios(callback: CallbackQuery):
    """Обновление списка сценариев"""
    keyboard = create_menu_scenarios_list_keyboard()
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer("🔄 Список обновлен")


@router.callback_query(F.data.in_(["no_scenarios", "error_scenarios"]))
async def handle_scenario_errors(callback: CallbackQuery):
    """Обработка ошибок сценариев"""
    await callback.answer("❌ Нет доступных сценариев или произошла ошибка", show_alert=True)