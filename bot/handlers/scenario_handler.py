from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
import os

from bot.states.user_state import UserState
from bot.utils.scenario_loader import load_scenario
from bot.keyboards.scenario_keyboards import create_theory_keyboard, create_practice_keyboard, create_branch_keyboard
from bot.config import IMAGE_DIR
router = Router()


async def send_scenario_step(message: Message, state: FSMContext):
    """Отправка текущего шага сценария с поддержкой локальных фото"""
    user_data = await state.get_data()
    scenario = user_data['scenario']
    current_step = user_data['current_step']

    if current_step >= len(scenario['steps']):
        await message.answer("🎉 Сценарий завершен! Можете начать заново командой /start_scenario",
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    step = scenario['steps'][current_step]
    has_photo = 'photo' in step and step['photo']

    # Функция для отправки сообщения с фото или без
    async def send_content(text: str, keyboard=None):
        if has_photo:
            # Формируем путь к локальному файлу
            photo_path = os.path.join(IMAGE_DIR, step['photo'])

            # Проверяем существование файла
            if not os.path.exists(photo_path):
                await message.answer(f"❌ Фото не найдено: {step['photo']}")
                # Отправляем только текст если фото нет
                await message.answer(text, reply_markup=keyboard)
                return

            # Создаем объект фото из локального файла
            photo = FSInputFile(photo_path)

            # Отправляем фото с текстом как подпись
            await message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=keyboard
            )
        else:
            # Отправляем только текст
            await message.answer(
                text=text,
                reply_markup=keyboard
            )

    # Обработка разных типов шагов
    if step['type'] == "theory":
        keyboard = create_theory_keyboard(current_step)
        await send_content(step['text'], keyboard)
        await state.set_state(UserState.in_scenario)

    elif step['type'] == "practice":
        keyboard = create_practice_keyboard(step['buttons'], current_step)
        await send_content(step['text'], keyboard)
        await state.set_state(UserState.waiting_answer)

    elif step['type'] == "text_answer":
        text = step['text']
        if 'placeholder' in step:
            text += f"\n\n💡 Подсказка: {step['placeholder']}"

        if has_photo:
            photo_path = os.path.join(IMAGE_DIR, step['photo'])
            if not os.path.exists(photo_path):
                await message.answer(f"❌ Фото не найдено: {step['photo']}")
                await message.answer(text, reply_markup=ReplyKeyboardRemove())
            else:
                photo = FSInputFile(photo_path)
                await message.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=ReplyKeyboardRemove()
                )
        else:
            await message.answer(text, reply_markup=ReplyKeyboardRemove())
        await state.set_state(UserState.waiting_text_input)

    elif step['type'] == "branch":
        keyboard = create_branch_keyboard(step['options'], current_step)
        await send_content(step['text'], keyboard)
        await state.set_state(UserState.waiting_branch)


# ... остальные обработчики без изменений ...


@router.callback_query(F.data.startswith("branch_"))
async def handle_branch_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора в развилке"""
    data_parts = callback.data.split("_")
    step_index = int(data_parts[1])
    option_index = int(data_parts[2]) - 1

    user_data = await state.get_data()
    scenario = user_data['scenario']
    step = scenario['steps'][step_index]

    selected_option = step['options'][option_index]
    response = selected_option['response']

    # Отправляем ответ на выбор
    await callback.message.answer(response)

    # Переходим к следующему шагу
    await state.update_data(current_step=step_index + 1)
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_scenario_step(callback.message, state)
    await callback.answer()


# ... остальные обработчики без изменений ...

@router.message(StateFilter(UserState.waiting_text_input))
async def handle_text_input(message: Message, state: FSMContext):
    """Обработка текстового ответа пользователя"""
    # Просто принимаем любой текст и переходим дальше
    await message.answer("✅ Спасибо за ваш ответ! Продолжаем...")

    user_data = await state.get_data()
    current_step = user_data['current_step']
    await state.update_data(current_step=current_step + 1)

    await send_scenario_step(message, state)


@router.message(Command("start_scenario"))
async def cmd_start_scenario(message: Message, state: FSMContext):
    """Начало сценария по умолчанию"""
    scenario = load_scenario("test")

    if not scenario:
        await message.answer("❌ Сценарий не найден")
        return

    await state.set_state(UserState.in_scenario)
    await state.update_data(
        scenario=scenario,
        current_step=0
    )

    await send_scenario_step(message, state)


@router.callback_query(F.data.startswith("next_"))
async def handle_next_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'дальше'"""
    next_step = int(callback.data.split("_")[1])

    await state.update_data(current_step=next_step)
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_scenario_step(callback.message, state)
    await callback.answer()


@router.callback_query(F.data.startswith("answer_"))
async def handle_answer_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка ответов на практические задания"""
    data_parts = callback.data.split("_")
    step_index = int(data_parts[1])
    user_answer = "_".join(data_parts[2:])

    user_data = await state.get_data()
    scenario = user_data['scenario']
    step = scenario['steps'][step_index]

    # Проверка ответа
    is_correct = user_answer == step.get('correct_answer', '')

    if is_correct:
        await callback.message.answer("✅ Правильно! Переходим дальше...")
        await state.update_data(current_step=step_index + 1)
        await callback.message.edit_reply_markup(reply_markup=None)
        await send_scenario_step(callback.message, state)
    else:
        await callback.answer("❌ Неправильно, попробуйте еще раз", show_alert=True)

    await callback.answer()
