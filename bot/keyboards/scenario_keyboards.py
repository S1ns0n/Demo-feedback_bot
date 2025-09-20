from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_theory_keyboard(step_index: int) -> InlineKeyboardMarkup:
    """Клавиатура для теоретического шага"""
    button = InlineKeyboardButton(
        text="дальше →",
        callback_data=f"next_{step_index + 1}"
    )
    return InlineKeyboardMarkup(inline_keyboard=[[button]])


def create_practice_keyboard(buttons: list, step_index: int) -> InlineKeyboardMarkup:
    """Клавиатура для практического задания"""
    keyboard_buttons = []

    for btn in buttons:
        keyboard_buttons.append(
            InlineKeyboardButton(
                text=btn,
                callback_data=f"answer_{step_index}_{btn}"
            )
        )

    # Разбиваем кнопки по 2 в ряд для лучшего вида
    rows = [keyboard_buttons[i:i + 2] for i in range(0, len(keyboard_buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)