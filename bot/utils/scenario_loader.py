import json
import os
import logging
from bot.config import SCENARIOS_DIR

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_scenario(scenario_name: str) -> dict | None:
    """
    Загрузка сценария из JSON файла с обработкой ошибок

    Args:
        scenario_name: Название сценария (без расширения .json)

    Returns:
        dict: Данные сценария или None при ошибке
    """
    try:
        file_path = os.path.join(SCENARIOS_DIR, f"{scenario_name}.json")

        # Проверка существования файла
        if not os.path.exists(file_path):
            logger.warning(f"Сценарий '{scenario_name}' не найден")
            return None

        # Чтение файла
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Валидация структуры сценария
        if not validate_scenario_structure(data):
            logger.error(f"Неверная структура сценария '{scenario_name}'")
            return None

        logger.info(f"Сценарий '{scenario_name}' успешно загружен")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка JSON в файле '{scenario_name}': {e}")
        return None
    except Exception as e:
        logger.error(f"Ошибка загрузки сценария '{scenario_name}': {e}")
        return None


def validate_scenario_structure(data: dict) -> bool:
    """
    Проверка базовой структуры сценария

    Args:
        data: Данные сценария

    Returns:
        bool: True если структура верная, False если есть ошибки
    """
    # Проверка обязательных полей
    required_fields = ['name', 'steps']
    if not all(field in data for field in required_fields):
        logger.error("Отсутствуют обязательные поля: 'name' или 'steps'")
        return False

    # Проверка типа поля steps
    if not isinstance(data['steps'], list):
        logger.error("Поле 'steps' должно быть списком")
        return False

    # Проверка что steps не пустой
    if len(data['steps']) == 0:
        logger.error("Сценарий не может быть пустым (steps пустой)")
        return False

    # Валидация каждого шага
    for i, step in enumerate(data['steps']):
        if not validate_step_structure(step):
            logger.error(f"Ошибка в шаге {i + 1}")
            return False

    return True


def validate_step_structure(step: dict) -> bool:
    """
    Валидация структуры отдельного шага

    Args:
        step: Данные шага

    Returns:
        bool: True если структура верная, False если есть ошибки
    """
    # Проверка обязательных полей для любого шага
    if 'type' not in step or 'text' not in step:
        logger.error("Отсутствуют обязательные поля: 'type' или 'text'")
        return False

    step_type = step['type']

    # Проверка поля photo (если есть)
    if 'photo' in step and step['photo']:
        if not isinstance(step['photo'], str):
            logger.error("Поле 'photo' должно быть строкой (имя файла)")
            return False

    # Проверка поля button_text (если есть)
    if 'button_text' in step and step['button_text']:
        if not isinstance(step['button_text'], str):
            logger.error("Поле 'button_text' должно быть строкой")
            return False

    # Валидация в зависимости от типа шага
    if step_type == "theory":
        return True  # Теория требует только текст

    elif step_type == "practice":
        # Практика требует кнопки и правильный ответ
        if 'buttons' not in step:
            logger.error("Для типа 'practice' отсутствует поле 'buttons'")
            return False

        if 'correct_answer' not in step:
            logger.error("Для типа 'practice' отсутствует поле 'correct_answer'")
            return False

        if not isinstance(step['buttons'], list) or len(step['buttons']) == 0:
            logger.error("Поле 'buttons' должно быть непустым списком")
            return False

        if step['correct_answer'] not in step['buttons']:
            logger.error("correct_answer должен быть одним из элементов buttons")
            return False

        return True

    elif step_type == "text_answer":
        return True  # Текстовый ответ требует только текст


    elif step_type == "branch":

        if 'options' not in step:
            logger.error("Для типа 'branch' отсутствует поле 'options'")

            return False

        if not isinstance(step['options'], list) or len(step['options']) == 0:
            logger.error("Поле 'options' должно быть непустым списком")

            return False

        for i, option in enumerate(step['options']):

            if 'text' not in option:
                logger.error(f"Опция {i + 1} отсутствует поле 'text'")

                return False

            if 'response' not in option:
                logger.error(f"Опция {i + 1} отсутствует поле 'response'")

                return False

            # Проверяем repeat_step если есть

            if 'repeat_step' in option and not isinstance(option['repeat_step'], bool):
                logger.error(f"Опция {i + 1}: поле 'repeat_step' должно быть boolean")

                return False

            # Проверяем show_continue_button если есть

            if 'show_continue_button' in option and not isinstance(option['show_continue_button'], bool):
                logger.error(f"Опция {i + 1}: поле 'show_continue_button' должно быть boolean")

                return False

        return True

    elif step_type == "survey":
        # Survey требует только buttons без correct_answer
        if 'buttons' not in step:
            logger.error("Для типа 'survey' отсутствует поле 'buttons'")
            return False

        if not isinstance(step['buttons'], list) or len(step['buttons']) == 0:
            logger.error("Поле 'buttons' должно быть непустым списком")
            return False

        return True

    else:
        logger.error(f"Неизвестный тип шага: '{step_type}'")
        return False


def get_available_scenarios() -> list:
    """
    Получение списка доступных сценариев

    Returns:
        list: Список названий сценариев (без расширения .json)
    """
    try:
        # Создаем директорию если её нет
        os.makedirs(SCENARIOS_DIR, exist_ok=True)

        # Получаем список файлов
        files = os.listdir(SCENARIOS_DIR)

        # Фильтруем только JSON файлы и убираем расширение
        scenarios = [f.replace('.json', '') for f in files if f.endswith('.json')]

        logger.info(f"Найдено сценариев: {len(scenarios)}")
        return scenarios

    except FileNotFoundError:
        logger.warning(f"Директория '{SCENARIOS_DIR}' не найдена, создаем...")
        os.makedirs(SCENARIOS_DIR, exist_ok=True)
        return []
    except Exception as e:
        logger.error(f"Ошибка при получении списка сценариев: {e}")
        return []
