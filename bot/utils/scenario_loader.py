import json
import os
from bot.config import SCENARIOS_DIR

def load_scenario(scenario_name: str) -> dict | None:
    """Загрузка сценария из JSON файла"""
    try:
        file_path = os.path.join(SCENARIOS_DIR, f"{scenario_name}.json")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def get_available_scenarios() -> list:
    """Получение списка доступных сценариев"""
    try:
        files = os.listdir(SCENARIOS_DIR)
        return [f.replace('.json', '') for f in files if f.endswith('.json')]
    except FileNotFoundError:
        return []