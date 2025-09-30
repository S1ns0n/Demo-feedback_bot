from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
from bot.config import SCENARIOS_DIR
from bot.utils.sorter import natural_sort_key



def admin_action_keyboard() -> InlineKeyboardMarkup:
    try:
        rows = []
        rows.append([InlineKeyboardButton(text="Удалить пользователя", callback_data=f"admin_user_delete")])
        rows.append([InlineKeyboardButton(text="Добавить пользователя", callback_data=f"admin_user_add")])
        return InlineKeyboardMarkup(inline_keyboard=rows)
    except:
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Ошибка загрузки", callback_data="error_scenarios")
        ]])