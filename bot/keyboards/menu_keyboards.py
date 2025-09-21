from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
from bot.config import SCENARIOS_DIR
from bot.utils.sorter import natural_sort_key


def create_menu_scenarios_list_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком всех доступных сценариев
    Кнопки по одной в ряд, отсортированные по алфавиту
    """
    try:
        if not os.path.exists(SCENARIOS_DIR):
            os.makedirs(SCENARIOS_DIR)
            return InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="❌ Нет сценариев", callback_data="no_scenarios")
            ]])

        files = os.listdir(SCENARIOS_DIR)
        json_files = [f for f in files if f.endswith('.json')]

        if not json_files:
            return InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="❌ Нет сценариев", callback_data="no_scenarios")
            ]])

        scenarios_data = []

        for file in json_files:
            scenario_name = file.replace('.json', '')
            file_path = os.path.join(SCENARIOS_DIR, file)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    scenario_data = json.load(f)

                display_name = scenario_data.get('name', scenario_name)

                if len(display_name) > 30:
                    display_name = display_name[:27] + "..."

            except (json.JSONDecodeError, KeyError, Exception) as e:
                # Если не удалось загрузить JSON, используем имя файла
                print(f"Ошибка загрузки сценария {file}: {e}")
                display_name = scenario_name
                if len(display_name) > 30:
                    display_name = display_name[:27] + "..."

            # Сохраняем данные для сортировки
            scenarios_data.append({
                'file_name': scenario_name,
                'display_name': display_name
            })

        scenarios_data.sort(key=lambda x: natural_sort_key(x['display_name']))



        rows = []

        rows.append([
            InlineKeyboardButton(text="📝 Содержание программы", callback_data="programm_list")
        ])
        for scenario in scenarios_data:
            rows.append([
                InlineKeyboardButton(
                    text=f"📄 {scenario['display_name']}",
                    callback_data=f"start_scenario_{scenario['file_name']}"
                )
            ])

        # rows.append([
        #     InlineKeyboardButton(text="🔄 Обновить список", callback_data="refresh_scenarios")
        # ])

        return InlineKeyboardMarkup(inline_keyboard=rows)

    except Exception as e:
        print(f"Ошибка при создании клавиатуры сценариев: {e}")
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Ошибка загрузки", callback_data="error_scenarios")
        ]])