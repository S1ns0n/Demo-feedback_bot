from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.utils import keyboard

from bot.keyboards.admin_keyboards import admin_action_keyboard
from bot.utils.scenario_loader import get_available_scenarios
from bot.utils.scenario_loader import load_scenario
from bot.handlers.scenario_handler import send_scenario_step
from bot.states.admin_state import AdminState
from bot.config import IMAGE_DIR
from bot.middlewares import exist_middleware


router = Router()





@router.message(Command("admin"))
async def admin_panel(message: Message, bot: Bot):
    """Команда начала админской работы с ботом"""

    if message.chat.id not in exist_middleware.get_admin_ids():
        return

    all_users: list = exist_middleware.get_whitelist()
    if all_users:
        users_text = "👥 Список пользователей с доступом:\n\n"
        for i, user in enumerate(all_users, 1):
            users_text += f"{i}. {user}\n"
    else:
        users_text = "📝 Список пользователей пуст"

    await message.answer(text=users_text, reply_markup=admin_action_keyboard())


@router.callback_query(F.data == "admin_user_delete")
async def admin_user_delete_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        await bot.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None)
    except:
        pass
    await state.set_state(AdminState.delete_user_id)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=f"Введите id пользователя, чтобы удалить его из списка")


    await callback.answer()

@router.message(AdminState.delete_user_id)
async def admin_user_delete_process(message: Message, bot: Bot, state: FSMContext):


    user_id = message.text.strip()
    whitelist = [str(user_id) for user_id in exist_middleware.get_whitelist()]
    if user_id not in whitelist:
        await message.answer(text="⚠️ Такого id нет в белом списке")
        await state.clear()
        await admin_panel(message, bot)
        return

    try:
        exist_middleware.remove_from_whitelist(int(message.text.strip()))
        await message.answer(text="✅ Пользователь удалён из белого списка")
        await state.clear()
    except:
        await message.answer(text="❌ Ошибка удаления пользователя")



@router.callback_query(F.data == "admin_user_add")
async def admin_user_add(callback: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        await bot.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None)
    except:
        pass
    await state.set_state(AdminState.add_user_id)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=f"Введите id пользователя, чтобы добавить его в белый список")


    await callback.answer()

@router.message(AdminState.add_user_id)
async def admin_user_add_process(message: Message, bot: Bot, state: FSMContext):
    user_id = message.text.strip()
    whitelist = [str(user_id) for user_id in exist_middleware.get_whitelist()]

    if user_id in whitelist:
        await message.answer(text="⚠️ Пользователь с таким id уже в белом списке")
        await state.clear()
        await admin_panel(message, bot)
        return

    try:
        exist_middleware.add_to_whitelist(int(message.text.strip()))
        await message.answer(text="✅ Пользователь добавлен в белый список")
        await state.clear()
    except:
        await message.answer(text="❌ Ошибка добавления пользователя")