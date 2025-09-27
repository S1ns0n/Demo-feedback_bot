from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
import os
from aiogram.enums import ParseMode

from bot.states.user_state import UserState
from bot.utils.scenario_loader import load_scenario
from bot.keyboards.scenario_keyboards import create_theory_keyboard, create_practice_keyboard, create_branch_keyboard, create_survey_keyboard, create_continue_keyboard
from bot.keyboards.menu_keyboards import go_to_menu_keyboard
from bot.config import IMAGE_DIR
router = Router()


async def send_scenario_step(message: Message, state: FSMContext):
    """Отправка текущего шага сценария"""
    user_data = await state.get_data()
    scenario = user_data['scenario']
    current_step = user_data['current_step']

    if current_step >= len(scenario['steps']):
        await message.answer("🎉 Раздел завершен! Можете вернуться к списку разделов командой /menu",
                             reply_markup=go_to_menu_keyboard())
        await state.clear()
        return

    step = scenario['steps'][current_step]
    has_photo = 'photo' in step and step['photo']

    async def send_content(text: str, keyboard=None):
        if has_photo:
            photo_path = os.path.join(IMAGE_DIR, step['photo'])
            if not os.path.exists(photo_path):
                await message.answer(f"❌ Фото не найдено: {step['photo']}", parse_mode=ParseMode.HTML)
                await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                return

            photo = FSInputFile(photo_path)
            await message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        else:
            await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    if step['type'] == "theory":
        # Проверяем, является ли сообщение конечным
        is_final = step.get('is_final', False)

        if is_final:
            # Для конечного сообщения используем специальную клавиатуру
            keyboard = go_to_menu_keyboard()
        else:
            # Для обычного сообщения
            button_text = step.get('button_text', 'дальше')
            keyboard = create_theory_keyboard(current_step, button_text)

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
                await message.answer(f"❌ Фото не найдено: {step['photo']}", parse_mode=ParseMode.HTML)
                await message.answer(text, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
            else:
                photo = FSInputFile(photo_path)
                await message.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=ReplyKeyboardRemove(),
                    parse_mode=ParseMode.HTML
                )
        else:
            await message.answer(text, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        await state.set_state(UserState.waiting_text_input)

    elif step['type'] == "branch":
        keyboard = create_branch_keyboard(step['options'], current_step)
        await send_content(step['text'], keyboard)
        await state.set_state(UserState.waiting_branch)

    elif step['type'] == "branch_with_input":
        keyboard = create_branch_keyboard(step['options'], current_step)
        await send_content(step['text'], keyboard)
        await state.set_state(UserState.waiting_branch)

    elif step['type'] == "survey":
        keyboard = create_survey_keyboard(step['buttons'], current_step)
        await send_content(step['text'], keyboard)
        await state.set_state(UserState.waiting_survey)


@router.callback_query(F.data.startswith("survey_"))
async def handle_survey_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка ответов в опросе (без проверки правильности)"""
    data_parts = callback.data.split("_")
    step_index = int(data_parts[1])
    user_answer = "_".join(data_parts[2:])

    # Просто принимаем любой ответ и переходим дальше
    await callback.answer("✅ Ответ принят!", parse_mode=ParseMode.HTML)

    await state.update_data(current_step=step_index + 1)
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_scenario_step(callback.message, state)


@router.callback_query(F.data.startswith("branch_"))
async def handle_branch_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора в развилке (общий для branch и branch_with_input)"""
    data_parts = callback.data.split("_")

    if len(data_parts) != 3:
        return

    try:
        step_index = int(data_parts[1])
        option_index = int(data_parts[2]) - 1
    except ValueError:
        return

    user_data = await state.get_data()
    scenario = user_data['scenario']
    step = scenario['steps'][step_index]

    selected_option = step['options'][option_index]
    response = selected_option['response'] if 'response' in selected_option else selected_option.get('input_prompt', '')

    # Определяем тип шага
    step_type = step['type']

    if step_type == "branch":
        # Существующая логика для обычного branch
        should_repeat = selected_option.get('repeat_step', False)
        show_continue = selected_option.get('show_continue_button', True)

        if should_repeat:
            await callback.message.edit_reply_markup(reply_markup=None)
            await callback.message.answer(response)
            await send_scenario_step(callback.message, state)
        else:
            await callback.message.edit_reply_markup(reply_markup=None)

            if show_continue:
                await callback.message.answer(response, reply_markup=create_continue_keyboard(step_index + 1))
                await state.update_data(next_step_after_branch=step_index + 1)
                await state.set_state(UserState.waiting_branch_continue)
            else:
                await callback.message.answer(response)
                await state.update_data(current_step=step_index + 1)
                await send_scenario_step(callback.message, state)

    elif step_type == "branch_with_input":
        # Новая логика для branch_with_input
        await callback.message.edit_reply_markup(reply_markup=None)

        # Сохраняем данные для текстового ввода
        await state.update_data(
            current_step=step_index,
            branch_input_prompt=selected_option['input_prompt'],
            next_step_after_input=step_index + 1
        )

        # Переходим к текстовому вводу
        await state.set_state(UserState.waiting_branch_input)
        await callback.message.answer(selected_option['input_prompt'], reply_markup=ReplyKeyboardRemove())

    await callback.answer()


@router.message(StateFilter(UserState.waiting_branch_input))
async def handle_branch_input(message: Message, state: FSMContext):
    """Обработка текстового ввода после branch_with_input"""
    user_data = await state.get_data()
    next_step = user_data['next_step_after_input']

    # Сохраняем ответ пользователя (опционально)
    # await state.update_data(user_input=message.text)

    # Переходим к следующему шагу
    await state.update_data(current_step=next_step)
    await send_scenario_step(message, state)


@router.callback_query(F.data.startswith("con_branch_"))
async def handle_branch_continue(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'дальше' после branch"""
    try:
        next_step = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Ошибка перехода")
        return

    # Переходим к следующему шагу
    await state.update_data(current_step=next_step)
    await state.set_state(UserState.in_scenario)
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_scenario_step(callback.message, state)
    await callback.answer()

@router.message(StateFilter(UserState.waiting_text_input))
async def handle_text_input(message: Message, state: FSMContext):
    """Обработка текстового ответа пользователя"""
    # Просто принимаем любой текст и переходим дальше
    user_data = await state.get_data()
    current_step = user_data['current_step']
    await state.update_data(current_step=current_step + 1)

    await send_scenario_step(message, state)


@router.message(Command("start_scenario"))
async def cmd_start_scenario(message: Message, state: FSMContext):
    """Начало сценария по умолчанию"""
    scenario = load_scenario("day_6")

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
        await callback.message.answer("✅ Правильно! Переходим дальше...", parse_mode=ParseMode.HTML)
        await state.update_data(current_step=step_index + 1)
        await callback.message.edit_reply_markup(reply_markup=None)
        await send_scenario_step(callback.message, state)
    else:
        await callback.answer("❌ Неправильно, попробуйте еще раз", show_alert=True, parse_mode=ParseMode.HTML)

    await callback.answer()
